Model: Composer 2.5 | Branch: feat/SPEC-03e-contracts-api

Context: read plans/M0/specs/SPEC-03e/spec.md,
docs/contracts/openapi.yaml,
docs/contracts/README.md,
docs/adr/ADR-004-fastapi-api.md,
docs/adr/ADR-018-studio-ui-kit.md,
docs/product/QUESTIONS.md (Q-43),
.cursor/rules/contracts.mdc,
contracts/.
Task: implement SPEC-03e exactly as specified.
Boundaries: change only `contracts/`, `docs/contracts/openapi.yaml`, `x-version` fields in `docs/contracts/**`, `docs/contracts/README.md`, and the SPEC-03 wording in `AGENTS.md` and `.cursor/rules/contracts.mdc`; change contracts only as this spec names (OpenAPI models, the diagnostic-run path, the 1.0.0 cut).
Tests: write the tests under "Tests" first, make them pass, run make check.
Rules: AGENTS.md and .cursor/rules apply; flag any new dependency; no secrets in code.
Report: changes made, tests added, any deviation from the spec and why.
