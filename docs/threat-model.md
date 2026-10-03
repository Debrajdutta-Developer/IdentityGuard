# IdentityGuard Threat Model

## Assets
- User identities
- Authentication sessions
- Device identity
- Privilege state
- Security audit events

## Detection goals
IdentityGuard identifies suspicious patterns such as repeated authentication failures, unfamiliar devices, rapid geographic changes, and unexpected privilege elevation.

## Trust boundaries
1. External authentication telemetry enters the API.
2. The API validates and normalizes event data.
3. The detection engine evaluates the event with identity context.
4. A future persistence layer stores the assessment.

## Security assumptions
- Incoming telemetry is authenticated by the upstream identity provider.
- A single signal is not treated as proof of compromise.
- Detection results are risk signals for investigation, not automatic attribution.

## Planned controls
- Signed event ingestion
- API authentication
- Rate limiting
- Persistent audit trail
- Role-based access control
- SPIFFE/SPIRE workload identity
