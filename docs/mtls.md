# SPIFFE mTLS

IdentityGuard includes an optional mTLS verification boundary.

SPIFFE X.509-SVIDs can authenticate workloads and establish mutual TLS channels. The SPIFFE Workload API also provides trust bundles used to validate SVIDs.

## Server TLS context

The app.mtls.build_server_context function creates a TLS 1.3 server context that requires a client certificate, loads the IdentityGuard certificate and private key, and validates clients against the configured trust bundle.

Example environment values:
- IDENTITYGUARD_TLS_CERT
- IDENTITYGUARD_TLS_KEY
- SPIFFE_TRUST_BUNDLE

Certificate and private-key material is never exposed by an API endpoint.

## Reverse-proxy deployments

If TLS is terminated by a trusted local proxy, SpiffeMTLSGuard can require an allow-listed SPIFFE ID in an identity header. The proxy must perform certificate and trust-bundle validation before forwarding the request.

Never accept a user-controlled SPIFFE identity header as proof of identity.

## Production model

SPIRE Agent supplies short-lived X.509-SVIDs and trust bundles through the Workload API. A deployment can use those credentials directly in the TLS layer or through a trusted proxy.

The mTLS boundary is optional so local development can continue without a running SPIRE deployment.
