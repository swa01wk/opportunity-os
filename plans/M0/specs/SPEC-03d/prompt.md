Model: Composer 2.5 | Branch: feat/SPEC-03d-contracts-media

Context: read plans/M0/specs/SPEC-03d/spec.md,
docs/contracts/media/,
docs/contracts/examples/odd-squares.video-spec.json,
docs/contracts/examples/invalid/manifest.json,
docs/adr/ADR-002-remotion-only-renderer.md,
.cursor/rules/contracts.mdc,
contracts/.
Task: implement SPEC-03d exactly as specified.
Boundaries: change only `contracts/`, and the regenerated `docs/contracts/media/` files (the change-log row is completed by SPEC-03e); change contracts only as this spec names (regenerate the media files; no shape change).
Tests: write the tests under "Tests" first, make them pass, run make check.
Rules: AGENTS.md and .cursor/rules apply; flag any new dependency; no secrets in code.
Report: changes made, tests added, any deviation from the spec and why.
