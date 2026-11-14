# SPEC-02: CI pipeline, security scans and branch rules
Milestone: M0 | Status: Draft (ready when SPEC-01a merges) | Layer: cross-cutting
Agent (if any): —
Requirements: NFR-05, NFR-06, NFR-13, NFR-18 | Feature: — (cross-cutting) | ADRs: ADR-019, ADR-022
Screens: — | Branch: `feat/SPEC-02-ci-pipeline`

## Goal
Every pull request runs the required checks on GitHub-hosted runners, including secret, dependency, image and static scans that ban executing generated content and browser automation, so nothing reaches `main` without them.

## Scope
In:
- `.github/workflows/pr.yml`: one job per required check in [TEST_STRATEGY.md](../../../TEST_STRATEGY.md#cicd-pipeline): `lint`, `types`, `test-backend`, `test-agent`, `test-media`, `test-web`, `contracts`, `conformance`, `e2e-smoke`, `render-fixture`, `migrations`, `images`, `security`. Each calls a `make` target; jobs with nothing to run yet pass with "0 tests" and are still reported. Path filters and caches keep the run under about 15 minutes.
- `security` job: gitleaks, Semgrep OSS with the repo rules below, pip-audit, `pnpm audit`, Trivy on built images, and a licence check of both lockfiles against an allowlist in `infra/ci/licences.yaml`.
- Semgrep rules in `infra/ci/semgrep/`: ban `eval`, `exec`, `compile`, `new Function`, `subprocess` and dynamic `import()` outside an allowlist; `dangerouslySetInnerHTML`; SQL built by string concatenation or f-strings; browser automation and scraping libraries (Playwright, Puppeteer, Selenium, BeautifulSoup crawlers) outside `e2e/` and the Remotion renderer in `media/scenes/render/` (NFR-18).
- `diff-cover` floors on changed code (backend domain 80%, web components 70%; TEST_STRATEGY.md levels).
- `main.yml`: build every image, start an ephemeral stack with fakes, smoke `/readyz` (ADR-022). `nightly.yml`: 20:30 UTC (02:00 IST), skipped when `main` has not changed. `weekly-eval.yml`: Sunday; no suites yet, live keys from Actions secrets only.
- `.github/CODEOWNERS` covers `agent/evals/`, `**/tests/**`, `e2e/`, `infra/ci/` and the workflows (C13 protection).
- Renovate config grouping weekly updates (ADR-019).

Out: adding the required checks to the `main` ruleset (your M0 task once this merges); release builds (SPEC-01b); the tests each job will later run (their specs).

## Design
- Workflows only call Make targets; no logic lives in YAML beyond setup and caching (ADR-019).
- Actions are pinned by commit SHA; `permissions:` default to `contents: read`.
- No contract or data changes. Expected diff: about 350 lines.

## Acceptance criteria
- AC1: Given a pull request, when CI runs, then all thirteen required check names in TEST_STRATEGY.md are reported, each by its own job.
- AC2 (NFR-06): Given a commit containing a string that matches a secret pattern, when the `security` job runs, then it fails and names the file and rule, without echoing the value.
- AC3 (NFR-05): Given code that passes model output, fetched text or a spec to `eval`, `exec`, `new Function`, `subprocess`, a dynamic import, `dangerouslySetInnerHTML` or string-built SQL, when Semgrep runs, then the `security` job fails with the rule ID.
- AC4 (NFR-18): Given an import of a browser automation or scraping library outside `e2e/` and the Remotion renderer, when Semgrep runs, then the job fails.
- AC5: Given a dependency whose licence is not on the allowlist, when the licence check runs, then the job fails and names the package and licence.
- AC6: Given a schedule trigger and no new commit on `main` since the last nightly run, when `nightly.yml` starts, then it exits without running suites.

## Tests
- T-32 static: Semgrep rule tests with positive and negative fixtures per rule under `infra/ci/semgrep/tests/` (AC3, AC4); a test that the job names in `pr.yml` equal the TEST_STRATEGY.md required-check list (AC1); `actionlint` on every workflow; gitleaks and licence-check fixtures (AC2, AC5).

## Observability
CI run summaries name each job and its make target. Minutes used are reviewed at each retro (TEST_STRATEGY.md).

## Dependencies
SPEC-01a. Contracts: none. Size M (2 spec-days). After merge: you add the thirteen required checks to the `main` ruleset (DELIVERY_PLAN.md M0 task).
