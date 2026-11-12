# ADR-012: Authentication provider
Status: Proposed — awaiting your decision (Q-22)    Date: 2026-11-12

## Context
R1 has one authenticated owner holding every responsibility (R-01, R-05), with MFA and no self-built password store (A-22). The API verifies a token on every request (NFR-04); the Studio is Next.js (ADR-005). Agents and services have their own non-human identities and can never approve (R-43). R4 multi-member workspaces are out of scope, but the choice should not block them.

## Options

| | A. Clerk | B. Auth0 (Okta) | C. AWS Cognito | D. Self-hosted (Keycloak / Authentik) |
|---|---|---|---|---|
| Next.js integration | First-class middleware and components | Good SDK | Workable (Amplify or OIDC libraries), more glue | OIDC libraries, more glue |
| FastAPI verification | JWKS-verified JWT | JWKS-verified JWT | JWKS-verified JWT | JWKS-verified JWT |
| MFA | Yes | Yes | Yes (TOTP, SMS) | Yes |
| Data location | Vendor-hosted (mostly US) | Vendor-hosted, region selectable on some plans | Same AWS region as the app if ADR-011 = A | Your host |
| Effort | Lowest | Low | Medium | Highest (another service to run and patch) |
| Cost at one user | Free tier | Free tier | Near zero | Hosting cost |
| R4 readiness | Organisations and roles built in | Organisations available | Groups; roles are ours | Full |

## Recommendation
**A. Clerk** for the least code and the best Next.js fit; the API only verifies a JWT, so swapping later is contained to the `IdentityProvider` adapter (ADR-009). Choose **C. Cognito** if you pick AWS and want all data, including the owner's identity, in one Mumbai account under one DPDP review.

## Decision
Pending your choice. Either way: owner identity is mapped to an internal `member` row; responsibilities and approvals are ours, never the provider's roles (R-05).
