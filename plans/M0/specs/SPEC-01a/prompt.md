Model: Composer 2.5 | Branch: feat/SPEC-01a-toolchain

Context: read plans/M0/specs/SPEC-01a/spec.md,
AGENTS.md,
docs/adr/ADR-001-modular-monolith-four-layers.md,
docs/adr/ADR-015-local-object-store.md,
docs/adr/ADR-016-observability-stack.md,
docs/adr/ADR-019-toolchain.md,
docs/adr/ADR-022-delivery-pipeline-local-hosting.md,
docs/architecture/TECH_STACK.md,
docs/architecture/SECURITY.md (Secrets and credentials).
Task: implement SPEC-01a exactly as specified.
Boundaries: change only the new code folders, `Makefile`, `compose.yaml`, `docker/`, `infra/`, `.env.example`, `.gitignore`, the root `pyproject.toml`, `uv.lock`, `package.json`, `pnpm-workspace.yaml`, `pnpm-lock.yaml`, `e2e/nfr/` and the AGENTS.md repo map if a path changes; do not change public contracts.
Tests: write the tests under "Tests" first, make them pass, run make check.
Rules: AGENTS.md and .cursor/rules apply; flag any new dependency; no secrets in code.
Report: changes made, tests added, any deviation from the spec and why.
