Model: Composer 2.5 | Branch: feat/SPEC-xx-<name>

Context: read plans/Mx/specs/SPEC-xx/spec.md, docs/contracts/<file>,
docs/adr/ADR-xxx.md, docs/design/screens/<S-xx file>,
docs/design/tokens.md and <relevant folders>.
Task: implement SPEC-xx exactly as specified.
Boundaries: change only <paths>; do not change public contracts.
Screens: match the screen's layout, copy and empty / loading / error states.
Rebuild it with the app's components and tokens; never copy its HTML.
Tests: write the tests under "Tests" first, make them pass, run make check.
Rules: AGENTS.md and .cursor/rules apply; flag any new dependency; no secrets in code.
Report: changes made, tests added, any deviation from the spec and why.
