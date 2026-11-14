# SPEC-07: Studio sign-in and app shell
Milestone: M0 | Status: Draft (ready when SPEC-06 merges) | Layer: frontend
Agent (if any): —
Requirements: R-01, R-05, R-61 | Feature: F-01, F-17 | ADRs: ADR-005, ADR-012, ADR-018
Screens: S-01 (docs/design/screens/S-01-shell.html) | Branch: `feat/SPEC-07-studio-shell`

## Goal
You sign in to the Studio through Keycloak with your authenticator, land in the app shell that shows who you are and your responsibilities, and get sent back to sign-in, without losing your place, when the session ends.

## Scope
In:
- Next.js App Router app in `web/` with Auth.js (generic OIDC, PKCE) against the `oos-studio` client. Tokens stay server-side in the Auth.js session (frontend.mdc Security); API calls go through a Next.js route handler that adds the bearer token (`web/app/api/oos/[...path]`), using the generated `openapi-fetch` client.
- S-01 states from its [UI_DESIGN row](../../../../docs/product/UI_DESIGN.md#empty-loading-and-error-states) and prototype: sign-in (ready), redirecting to sign-in (loading), sign-in needs your authenticator (error), your session ended with the page you were on and "Sign in and return" (error). Copy as in the prototype.
- App shell (Studio frame, [UI_DESIGN](../../../../docs/product/UI_DESIGN.md#studio-frame-shared-on-every-screen)): left nav (Projects, Slate, Library, Runs), environment badge (`local` / `staging` from config), signed-in member with "Owner · 5 roles" from `/v1/me`, sign-out. Layout as in the S-02 and S-13 prototypes' frame.
- Nav destinations not built yet show the shared **unavailable** state with its reason ("Built in M2"), never an empty list (R-61 AC2).
- Problem mapping for this spec: 401 → re-authenticate and return to the same path; 403 `not_a_member` → "Your account is not a member of this workspace"; 5xx → retry with the request ID.
- Studio tokens and both themes from [tokens.md](../../../../docs/design/tokens.md); strings in `web/lib/strings.ts`; Atkinson Hyperlegible Next fonts self-hosted.

Out: project header, gate strip, spend meter, run indicator, approval dialog, error panel (SPEC-34, SPEC-35); the Projects screen (SPEC-36); the System check panel (SPEC-13).

## Design
- Components in `web/components/` (Radix primitives, shadcn pattern, ADR-018). The shell is built once and reused by every later screen.
- Session expiry keeps the return path; nothing in the Studio is reachable before sign-in (middleware on every route).
- Expected diff: about 400 lines.

## Acceptance criteria
- AC1 (R-01 AC1): Given no session, when any Studio route is opened, then the browser is redirected to Keycloak and no Studio content or API data is shown.
- AC2 (R-05 AC2): Given the seeded owner signs in with password and TOTP, then the shell shows the display name, "Owner · 5 roles", the environment badge and the four nav items.
- AC3: Given an account without an authenticator, when sign-in fails for MFA, then the "Sign-in needs your authenticator" state shows with "Set up authenticator".
- AC4: Given a session that expires on a page, when the next request gets 401, then "Your session ended" shows the page name and "Sign in and return" returns to that path after sign-in.
- AC5 (R-61 AC2): Given a nav destination not built yet, when opened, then it shows the unavailable state with its reason, not an empty list.
- AC6: Given the browser, then no access or refresh token is readable from client JavaScript or `localStorage`.

## Tests
- T-15 Playwright (S-01): every state above, copy, keyboard path through sign-in and the nav, axe in both themes, visual baseline from screenshots you approve in the PR (AC1–AC5).
- T-36 Playwright part: unauthenticated routes redirect; tokens absent from `document.cookie`-readable and `localStorage` (AC1, AC6).
- Vitest in `web/tests/`: problem-response mapping and the return-path helper.

## Observability
Browser OpenTelemetry is wired by SPEC-08; this spec emits the log event `auth.callback_failed` (reason only) from the Next.js server.

## Dependencies
SPEC-06 (and so SPEC-04, SPEC-03e for the generated client). Contracts: 1.0.0. Size M (2 spec-days).
