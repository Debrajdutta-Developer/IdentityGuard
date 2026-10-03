# IdentityGuard Enterprise Product Roadmap

IdentityGuard is being developed as a B2B identity threat detection and response platform.

## Product workflow

Company onboarding -> tenant -> identity/workload telemetry -> detection -> risk decision -> alert -> investigation -> response -> immutable audit evidence.

## Current foundation

- Tenant-scoped authentication telemetry
- Identity/device context
- Detection rules
- Risk scoring
- Explicit allow / step-up / deny decision contract
- Tenant-scoped audit ledger
- API-key authentication
- SPIFFE/SPIRE workload identity integration

## Next production capabilities

1. PostgreSQL persistence and migrations
2. Organization and user administration
3. API-key creation, hashing, expiry and rotation
4. Idempotent event ingestion
5. Alert lifecycle: open, acknowledged, resolved
6. Investigation endpoints and evidence timelines
7. Webhook/SIEM export
8. Redis-backed distributed rate limiting
9. Structured JSON logging and metrics
10. Production Docker and deployment configuration
11. Security testing, load testing and operational runbooks

## Product boundary

The platform is for authorized defensive security monitoring. It should integrate with an organization's existing identity provider, applications, SIEM and workload identity infrastructure rather than attempting unauthorized access.

## Delivery principle

A capability is considered production-oriented only after it has tests, explicit failure behavior, operational documentation and a deployment path. The project should not claim enterprise readiness merely because a feature exists in code.
