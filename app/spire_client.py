import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass

@dataclass(frozen=True)
class SpireIdentity:
    spiffe_id: str
    source: str = "spire-agent"

class SpireUnavailable(RuntimeError):
    pass

def fetch_spiffe_identity() -> SpireIdentity:
    binary = shutil.which("spire-agent")
    socket = os.getenv("SPIFFE_ENDPOINT_SOCKET", "unix:///tmp/spire-agent/public/api.sock")
    if not binary:
        raise SpireUnavailable("spire-agent binary is not installed")
    if not socket.startswith(("unix://", "tcp://")):
        raise SpireUnavailable("SPIFFE_ENDPOINT_SOCKET must use unix:// or tcp://")
    with tempfile.TemporaryDirectory(prefix="identityguard-svid-") as directory:
        socket_path = socket.removeprefix("unix://")
        result = subprocess.run(
            [binary, "api", "fetch", "x509", "-socketPath", socket_path, "-write", directory, "-silent"],
            capture_output=True, text=True, timeout=5, check=False,
        )
        if result.returncode != 0:
            raise SpireUnavailable("SPIRE Workload API is unavailable")
        cert_files = [os.path.join(directory, name) for name in os.listdir(directory)
                      if name.startswith("svid.") and name.endswith(".pem")]
        if not cert_files:
            raise SpireUnavailable("SPIRE returned no X.509-SVID")
        from cryptography import x509
        with open(cert_files[0], "rb") as cert_file:
            certificate = x509.load_pem_x509_certificate(cert_file.read())
        san = certificate.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
        ids = [str(v.value) for v in san if isinstance(v, x509.UniformResourceIdentifier)
               and str(v.value).startswith("spiffe://")]
        if len(ids) != 1:
            raise SpireUnavailable("SVID must contain exactly one SPIFFE ID")
        return SpireIdentity(ids[0])
