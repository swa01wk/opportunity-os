# SPEC-06: API authentication, members and responsibilities
Milestone: M0 | Status: Draft (ready when SPEC-04 and SPEC-03e merge) | Layer: backend
Agent (if any): —
Requirements: R-01, R-05, NFR-04 | Feature: F-01, F-12 | ADRs: ADR-012, ADR-004, ADR-009
Screens: — | Branch: `feat/SPEC-06-api-auth`

## Goal
Every API request except health checks needs a valid Keycloak access token for a member of the workspace, and each action is checked against the responsibility matrix, so services and agents can never act as people.

## Scope
In:
- Keycloak realm config in `infra/keycloak/` (no users, no secrets): realm `oos`, TOTP required, client `oos-studio` (authorization code + PKCE), audience `oos-api`, session lengths from [SECURITY.md](../../../../docs/architecture/SECURITY.md#authentication-and-roles) (access 10 min, rotating refresh, idle 12 h, absolute 7 days). Imported at `make up`.
- Seed step (dev and staging only): creates a synthetic Keycloak owner user from `.env` (`KEYCLOAK_DEV_OWNER_EMAIL`, `KEYCLOAK_DEV_OWNER_PASSWORD`, placeholders in `.env.example`) and the matching `app.member` with all five responsibilities.
- `IdentityProvider` port: JWKS verification (PyJWT), issuer, audience, `exp`, `nbf`, algorithm allowlist; a fake for tests that refuses to start unless `APP_ENV=test` (TH-01).
- Member resolution by `(iss, sub)`; unknown subject → 403 `not_a_member`. The workspace ID from the member is set on the DB session (SPEC-04 helper).
- `domain/authz.py`: the responsibility → action matrix from SECURITY.md as data, and a `require(action)` dependency; service and agent-task identities fail every member-only action (R-43). Step-up helper: actions marked step-up need `auth_time` within 15 minutes, else 403 `step_up_required`.
- `GET /v1/me` per `openapi.yaml` 1.0.0. RFC 9457 problem responses with the error class (backend.mdc). Every route except `/healthz` and `/readyz` requires authentication.

Out: the Studio sign-in (SPEC-07); approvals (SPEC-28); any step-up action (their specs).

## Design
- Matrix is owned by SECURITY.md; the code mirrors it and a test compares the two.
- Expected diff: about 380 lines.

## Acceptance criteria
- AC1 (R-01 AC1, NFR-04): Given a request with no token, a forged signature, `alg: none`, a wrong audience or an expired token, when it targets any route except health checks, then it gets 401 and no workspace data.
- AC2: Given a valid token whose subject is not a member, when it calls `/v1/me`, then it gets 403 `not_a_member`.
- AC3 (R-05 AC1): Given each row of the SECURITY.md matrix, when an identity without the needed responsibility attempts the action, then it gets 403 naming the responsibility needed; service and agent-task identities are refused every member-only action (R-43).
- AC4 (R-05 AC2): Given the seeded owner, when calling `/v1/me`, then the response lists the workspace and all five responsibilities.
- AC5: Given a step-up action and `auth_time` older than 15 minutes, when attempted, then 403 `step_up_required`.
- AC6 (TH-01): Given `APP_ENV` other than `test`, when the fake identity provider is configured, then the API refuses to start.

## Tests
- T-36 functional: missing, forged, `alg: none`, wrong-audience and expired tokens; not-a-member; fake IdP outside test; step-up helper (AC1, AC2, AC5, AC6).
- T-37 functional: the matrix enforced per row, the code matrix equals the SECURITY.md table, service and agent identities refused (AC3, AC4).

## Observability
Log events `authz.denied` (action, responsibility needed, member UUID) and `auth.token_rejected` (reason, no token); metric `oos.authz.denied{action}`. No emails or names in telemetry (OBSERVABILITY.md redaction).

## Dependencies
SPEC-04 (members, session helper), SPEC-03e (`/me` and problem schemas in 1.0.0). Contracts: 1.0.0. Size M (2 spec-days).
