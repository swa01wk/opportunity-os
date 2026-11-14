Model: Composer 2.5 | Branch: feat/SPEC-01b-release-host

Context: read plans/M0/specs/SPEC-01b/spec.md,
docs/adr/ADR-022-delivery-pipeline-local-hosting.md,
plans/TEST_STRATEGY.md (Environments, CI/CD pipeline),
docs/architecture/SECURITY.md (Secrets and credentials),
Makefile,
compose.yaml.
Task: implement SPEC-01b exactly as specified.
Boundaries: change only `infra/release/`, `releases/README.md`, `Makefile`, `.env.staging.example`, `.env.production.example` and `.gitignore`; do not change public contracts.
Tests: write the tests under "Tests" first, make them pass, run make check.
Rules: AGENTS.md and .cursor/rules apply; flag any new dependency; no secrets in code.
Report: changes made, tests added, any deviation from the spec and why.
