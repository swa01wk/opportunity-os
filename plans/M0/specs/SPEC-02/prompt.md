Model: Composer 2.5 | Branch: feat/SPEC-02-ci-pipeline

Context: read plans/M0/specs/SPEC-02/spec.md,
plans/TEST_STRATEGY.md (What runs when, CI/CD pipeline),
docs/adr/ADR-019-toolchain.md,
docs/adr/ADR-022-delivery-pipeline-local-hosting.md,
AGENTS.md (Never),
.github/,
Makefile.
Task: implement SPEC-02 exactly as specified.
Boundaries: change only `.github/workflows/`, `.github/CODEOWNERS`, `infra/ci/`, `renovate.json` and `Makefile` targets the jobs call; do not change public contracts.
Tests: write the tests under "Tests" first, make them pass, run make check.
Rules: AGENTS.md and .cursor/rules apply; flag any new dependency; no secrets in code.
Report: changes made, tests added, any deviation from the spec and why.
