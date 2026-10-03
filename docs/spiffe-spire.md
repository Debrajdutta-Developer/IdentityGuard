# SPIFFE/SPIRE Integration

IdentityGuard now has a workload-identity abstraction using the SPIFFE_ID environment variable.

Example environment value:
SPIFFE_ID=spiffe://identityguard.example/api

The API exposes workload identity status at:
GET /api/v1/identity/workload

Important: this MVP does not claim that an environment variable proves a real SPIRE-issued identity. It only creates the application boundary for a later SPIFFE Workload API integration.

Planned production integration:
1. Connect to the SPIRE Agent Workload API.
2. Obtain an X.509-SVID.
3. Validate the trust bundle.
4. Use the SVID for service-to-service authentication.
5. Rotate credentials through SPIRE.

A manually supplied SPIFFE_ID must not be treated as cryptographic authentication.
