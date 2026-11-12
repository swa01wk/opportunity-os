# ADR-012: Keycloak (OIDC) locally; Amazon Cognito when hosted
Status: Accepted    Date: 2026-11-12 (decided by the product owner; Q-22: "best for local now, Cognito when we scale")

## Context
R1 has one authenticated owner who holds every responsibility (R-01, R-05). The owner needs MFA, and the product must not keep its own password store (A-22). The API verifies a token on every request (NFR-04). Services and agent tasks have non-human identities and can never approve (R-43). The system runs locally first and on AWS later (ADR-011), so moving to Cognito must be a configuration change, not a rewrite.

## Decision
- **Local: Keycloak** runs in Docker Compose with one realm and one confidential client for the Studio. The owner account has TOTP MFA required. The realm export is committed with **no users and no secrets**; `make setup` creates the owner from `.env` values.
- **Hosted: an Amazon Cognito user pool** in ap-south-1, with MFA required and the hosted login.
- **One protocol: OpenID Connect, authorization-code flow with PKCE.**
  - `web` uses Auth.js with a generic OIDC provider (issuer, client ID and secret from env).
  - `api` verifies the access token against the issuer's JWKS (signature, `iss`, `exp`, `token_use`) in the `IdentityProvider` adapter (ADR-009).
  - The adapter maps provider-specific claims to one internal `Principal`. For example, Cognito access tokens carry `client_id` where Keycloak carries `aud`, and MFA appears as `amr` in Keycloak but is enforced by pool policy in Cognito.
- **Tests:** a fake `IdentityProvider` signs tokens with a test key. It is enabled only when `APP_ENV=test`, and the API refuses to start with it in any other environment.
- Responsibilities and approvals live in our `member` table, never in Keycloak roles or Cognito groups (R-05).

## Alternatives
- **A development bypass (no real login locally):** fastest, but local behaviour would differ from hosted and could not prove R-01 AC1 / NFR-04. Rejected for everything except automated tests.
- **Cognito from day one:** needs an AWS account and internet access before anything is hosted (ADR-011).
- **Clerk or Auth0:** a second vendor to migrate away from when moving to Cognito.

## Consequences
- Easier: real login and MFA locally; switching to Cognito changes only issuer, client and claim-mapping configuration.
- Harder: Keycloak adds one more container (about 0.5–1 GB RAM) to the local stack.
- Must do: when AWS arrives, re-create the owner in Cognito and re-link `member.idp_issuer` / `idp_subject`. This is a one-row update for one owner, done in the AWS migration spec.
