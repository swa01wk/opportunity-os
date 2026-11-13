# ADR-019: Build and test toolchain
Status: Accepted    Date: 2026-11-13

## Context
Engineers, CI and Cursor must run the same commands (PROCESS "Make and Docker"); the host needs only Docker, make and git. Two languages (ADR-001). PROCESS's testing table lists example tools and says to pick them in TECH_STACK.md.

## Decision
- **Python:** `uv` for environments and the lockfile; Ruff for lint and format; mypy (strict on `contracts/` and `backend/` domain code); pytest with pytest-asyncio, httpx and Testcontainers (PostgreSQL) for functional tests; Hypothesis for demonstration functions.
- **TypeScript:** pnpm workspaces (`web`, `media/scenes`, `contracts/ts`); ESLint (with jsx-a11y) and Prettier; `tsc --noEmit`; Vitest with Testing Library; Playwright for integration, E2E and screenshot checks against S-xx; axe-core in Playwright for accessibility.
- **Contracts:** Pydantic → JSON Schema → `json-schema-to-typescript`; Ajv for runtime checks (ADR-008).
- **Security in CI:** gitleaks (secrets), pip-audit and `pnpm audit` (dependencies), Semgrep OSS (static analysis), Trivy (images), a licence check of both lockfiles.
- **Dependency updates:** Renovate, merged through normal PRs.
- **Everything runs inside containers** via the Makefile; CI calls the same targets.

## Alternatives
- **Poetry / pip-tools:** slower; uv covers locking and Python version pinning.
- **Biome instead of ESLint + Prettier:** faster, but weaker accessibility lint coverage today.
- **npm or Yarn:** pnpm's workspace and disk behaviour suit the three TS packages.

## Consequences
- Easier: one command set for humans, CI and Cursor.
- Harder: two toolchains to keep current; Renovate groups updates weekly.

## Amendment (Stage 3, 2026-11-14)
- **Non-functional tools:** k6 for load tests on key API flows and OWASP ZAP baseline scans of `web` and `api`, run per milestone on staging and in hardening only (TEST_STRATEGY.md).
- **Coverage on changed code:** `diff-cover` over pytest and Vitest coverage reports enforces the floors in TEST_STRATEGY.md on every PR.
