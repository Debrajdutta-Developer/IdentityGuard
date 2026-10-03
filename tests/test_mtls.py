import ssl
import pytest
from app.mtls import MTLSConfigurationError, build_server_context

def test_missing_mtls_files_raise(tmp_path):
    with pytest.raises(MTLSConfigurationError):
        build_server_context(
            str(tmp_path / "cert.pem"),
            str(tmp_path / "key.pem"),
            str(tmp_path / "bundle.pem"),
        )

def test_tls_version_requirement():
    assert ssl.TLSVersion.TLSv1_3.value >= ssl.TLSVersion.TLSv1_2.value
