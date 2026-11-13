# Product Delivery Process

Nov 12, 2026 · @Swaroop Shivakumar

## Purpose and principles

This process takes a client or product-team PRD to a released product one milestone at a time. Cursor implements the code, CI and Claude review it, and a human approves every merge. It fits products with a backend, a frontend and, optionally, an AI agent.

1. **The PRD is input, owned by the product owner.** Store it in `docs/sources/` and derive your own `REQUIREMENTS.md` from it. It changes only when the product owner decides: during discovery (until G3) it may be revised in place with a dated revision note; after that, through change control.
2. **One owner per fact.** Each requirement, decision or threshold lives in one doc; other docs link to it.
3. **Traceable IDs end to end.** PRD section → `R-xx` → component, screen S-xx and `ADR-xxx` → `SPEC-xx` → `T-xx`.
4. **Decisions are recorded when made**, as ADRs, not as a later stage.
5. **Contracts before code.** API, event and agent-tool schemas are agreed before backend, frontend and agent work splits.
6. **Shift left.** Test harnesses, security checks and observability are built in M0, not added at the end.
7. **Small, reversible changes.** One spec = one short-lived branch = one PR.
8. **AI writes, humans own.** AI review assists; a person is accountable for every merge.
9. **`STATUS.md` is the single entry point** for anyone asking where the product stands.

## Lifecycle at a glance

There are seven stages, each closed by a gate. Stages 1–3 run once per product and again for each change request. Stages 4–6 repeat for every milestone.

| # | Stage | Question it answers | Owning docs | Gate |
| --- | --- | --- | --- | --- |
| 1 | Intake | Who is it for, what does it solve, and what exactly must we build? | Product framing in the PRD or `REQUIREMENTS.md`, `REQUIREMENTS.md`, `QUESTIONS.md`, `DISCOVERY.md` | G1 Requirements baseline signed off |
| 2 | Design | How will it work? | `ARCHITECTURE.md`, ADRs, contracts, `UI_DESIGN.md`, Claude Design canvas, screens (docs/design/), `TECH_STACK.md`, `SECURITY.md`, `OBSERVABILITY.md` | G2 Design review passed, screens approved |
| 3 | Plan | In what order, and how do we prove it? | `DEVELOPMENT_PLAN.md`, `TEST_STRATEGY.md`, `DELIVERY_PLAN.md` | G3 Milestone scope and dates agreed |
| 4 | Build | What is being built now? | `plans/Mx/specs/`, PRs, `STATUS.md` | Each spec meets its Definition of Done |
| 5 | Verify | Does the milestone meet the requirements? | E2E and eval reports, UAT notes | G4 Milestone exit checklist met |
| 6 | Release | Is it safe to ship and run? | `RELEASE_NOTES.md`, `CHANGELOG.md`, `RUNBOOK.md` | G5 Go-live approved |
| 7 | Learn and change | What changes next? | `plans/retros/`, change requests | Changes re-enter at stage 1 |

**Gate owners.** Every gate names who signs it, and `STATUS.md` records each approval with its date:

- G1: the client's product owner and your tech lead;
- G2: your tech lead for the design, the client for the screens;
- G3: the client for scope and dates;
- G4: the client for UAT, your tech lead for the checklist;
- G5: the client and whoever will run production.

## Stage 1 — Requirements intake

The first output is your own requirements baseline, derived from the PRD and confirmed by the client before any design starts.

**Inputs:** the PRD (versioned in `docs/sources/`, revised only by the product owner), any client designs, and access to existing systems.

**Product framing first.** Before writing requirements, make sure the product concepts below exist, because requirements, screens and tests all trace back to them. Keep the PRD's own IDs where it has them; where it lacks one, propose it in `REQUIREMENTS.md` and raise a `Q-xx`.

- **Personas** (`P-xx` or the PRD's IDs): who uses the product, their job, difficulties and what success means. Personas are not roles.
- **User journeys** (`J-xx`): trigger, sequence of steps, branches and outcome, each with its release.
- **User stories** (`US-xx`): "As <persona>, I want <capability> so that <outcome>", with release, journey and acceptance.
- **Value and defensibility**: the problems the product solves, how each is solved and the evidence that proves it; and the moat hypotheses, in the order they would be earned, each with its proof checkpoint. These are hypotheses, never claims, until their proof is met.

1. Break the PRD into atomic requirements:
   - functional `R-xx`;
   - non-functional `NFR-xx`: performance, security, availability, accessibility, languages, compliance, AI quality.
2. Give each requirement its PRD section, a priority (Must, Should, Could, Won't) and acceptance criteria in Given / When / Then form.
3. Group requirements into features `F-xx`. Features become specs in stage 3.
4. Log every gap or ambiguity as `Q-xx`, with the assumption `A-xx` you will build on if nobody answers.
5. If an existing system is involved, write `DISCOVERY.md`: current behaviour, integration points, constraints.
6. Record the PRD's success metrics as `KPI-xx`, each with a target and how it will be measured. They become analytics events in stage 2 and are reviewed after release.

**Outputs:** `REQUIREMENTS.md`, `QUESTIONS.md`, and `DISCOVERY.md` when needed.

**Gate G1:**

- personas, journeys, stories and the value and defensibility hypotheses exist and the client has confirmed them;
- every user-facing Must `R-xx` traces to a user story and its journey;
- every PRD section maps to at least one `R-xx` or is listed as out of scope;
- every Must has acceptance criteria;
- the client has answered the questions or accepted the assumptions.

## Stage 2 — Design

Design produces the architecture and its decisions together. Then come the contracts that let backend, frontend and agent work proceed in parallel. Docs at the same step can be written at the same time.

| Step | Doc | Contents | Done when |
| --- | --- | --- | --- |
| 1 | `ARCHITECTURE.md` | Context, containers and components (C4 levels 1–3), data model, write path, migration of any existing data, quality scenarios for each NFR | Every `R-xx` maps to a component |
| 1 | `docs/adr/ADR-xxx.md` | One ADR per significant choice, written when the choice is made | No open choice blocks M0 |
| 2 | `docs/contracts/` | OpenAPI spec, event schemas, agent tool schemas, DB schema draft | Backend, frontend and agent can each mock the others |
| 3 | `UI_DESIGN.md` | Journeys in scope and their steps, the stories and problem each screen serves, screens, flows, empty / loading / error states, accessibility, languages | Every user-facing `R-xx` and every in-scope journey step maps to a screen |
| 3 | `TECH_STACK.md` | Tools and versions per layer, each linked to its ADR; a monthly cost estimate for infrastructure and model usage | Every layer has a chosen tool |
| 4 | `SECURITY.md` | Threat model (STRIDE), auth and roles, data classification, secrets, personal-data handling and retention under the applicable law (for example India's DPDP Act or GDPR); for agents, prompt injection and excessive agency | Threats have mitigations or accepted risks |
| 4 | `OBSERVABILITY.md` | Signals per component, SLOs, alerts, retention, PII redaction, product analytics events for each KPI-xx | Every key journey has an SLO |

**Screens (step 5, after `UI_DESIGN.md`).** Screens are designed by journey in Claude Design, reviewed there by the client, then committed to the repo as HTML prototypes. Cursor later rebuilds them as production code, so the approved screens are the visual source of truth for every frontend spec.

1. **Design in Claude Design.** One canvas per screens version, using `docs/design/tokens.md`:
   - a page mapping journeys → steps → stories → screens, and what is out of scope;
   - a page on what the product solves: problems → screens → `KPI-xx`, and the moat hypotheses with their proof checkpoints;
   - one page per journey, screens in step order, joined by links so the client can click through each journey in Play;
   - under each screen, a note naming its journey step, stories, gate, `R-xx`, the problem it solves, the moat it builds and the states still to come.
2. **Client review on the canvas.** The client comments on the canvas; screens are revised there until approved. `STATUS.md` links the canvas.
3. **HTML in the repo.** Each approved screen is built as a self-contained HTML prototype that matches the canvas, with realistic synthetic data and its empty, loading and error states.

- Each screen gets an ID `S-xx`, listed in `UI_DESIGN.md` with its journey step, stories, `R-xx` and file path (`docs/design/screens/S-xx-<name>.html`).
- Each prototype shows realistic sample data and its empty, loading and error states.
- Shared colours, type and spacing go in `docs/design/tokens.md`, so every screen and every Cursor run uses the same values.
- Screens go through the normal loop: a `design/screens-<version>` branch, a PR, client review, then merge.
- `STATUS.md` tracks each screen: Draft → Client review → Approved → Built. Once approved, a screen changes only through change control.

The trace for UI work is `J-xx` / `US-xx` → `R-xx` → `S-xx` → frontend `SPEC-xx` → Playwright `T-xx`.

**Gate G2 (design review):**

- traceability is complete;
- contracts are versioned;
- the threat model is reviewed and the client has approved the screens on the canvas, journey by journey;
- the HTML prototypes match the approved canvas;
- nothing is designed that no requirement asks for.

## Stage 3 — Plan

Planning turns the design into three things: an ordered spec backlog, a test strategy with CI/CD gates, and a milestone schedule the client agrees to. The development plan is the engineering view; the delivery plan is the client view.

| Doc | Audience | Contents |
| --- | --- | --- |
| `DEVELOPMENT_PLAN.md` | Engineers | Features split into specs `SPEC-xx`, each one PR of about 1–3 days; dependency order, the screens S-xx each frontend spec builds, and which specs run in parallel; branch naming, coding standards, the Cursor and Claude workflow |
| `TEST_STRATEGY.md` | Engineers, QA | Test levels and owners; what runs per PR, nightly and per milestone; eval suites, thresholds and test data; Definition of Done; CI/CD pipeline and environments |
| `DELIVERY_PLAN.md` | Client, product | Milestones M0–Mn with the `R-xx` each delivers; dates, demo and UAT slots; risks, assumptions, issues and dependencies (RAID) |

**Agent rules.** Stage 3 also writes the instructions every Cursor run follows. They are derived from `TECH_STACK.md`, `ARCHITECTURE.md`, the ADRs and the development plan, and committed in M0. Write each rule as an `.mdc` file with frontmatter (`description`, `globs`, `alwaysApply`) so it loads only where it applies, and keep shared, unscoped instructions in `AGENTS.md` ([Cursor docs](https://cursor.com/docs/rules)).

| File | Applies when | Holds |
| --- | --- | --- |
| `AGENTS.md` (repo root) | Every agent run | Product summary, repo map, the make targets (setup, up, test, lint, check), where specs and contracts live, global don'ts |
| `.cursor/rules/000-core.mdc` | Always (`alwaysApply: true`) | Coding standards, ID conventions, branch and commit rules, "never change a contract outside a spec" |
| `.cursor/rules/backend.mdc` | `globs: backend/**` | Layering, error handling, database and migration rules, test style |
| `.cursor/rules/frontend.mdc` | `globs: web/**` | Component and state patterns; screens in docs/design/screens/ are the visual reference, rebuilt with the app's components and tokens, never copied; accessibility, languages, test style |
| `.cursor/rules/agent.mdc` | `globs: agent/**` | Prompt and tool conventions, model mocking, eval scenario format |
| `.cursor/rules/testing.mdc` | `globs: **/tests/**` | Test levels, fixtures, `T-xx` naming |
| `.cursor/rules/observability.mdc` | Code that adds a flow | Span, log and metric conventions |
| `CLAUDE.md` | Claude PR review | Review checklist; points to `AGENTS.md` so both tools share the same conventions |

Each rule states the decision and links its ADR for the reason. Keep each under 500 lines. When Cursor or the review repeats a mistake, fix the rule in the same PR.

**Gate G3:**

- every Must `R-xx` is in a milestone;
- every spec lists its `R-xx` and `T-xx`, and every frontend spec its approved `S-xx`;
- the client agrees what is in each milestone and when.

## Milestones

Every product starts with M0, a walking skeleton that proves the pipeline end to end. Feature milestones follow, each a demoable vertical slice of PRD features. A hardening milestone closes the project.

| Milestone | Delivers | Exit criterion |
| --- | --- | --- |
| M0 Foundation | Repo, Makefile and Docker Compose stack, CI/CD, dev and staging environments, auth skeleton, database and migrations, observability wiring, contract stubs, AGENTS.md and Cursor rules, test harnesses (unit, integration, Playwright, agent mock and eval runner) | One trivial request goes frontend → backend → agent → database, traced, and is deployed by the pipeline; a fresh clone runs with make setup and make up |
| M1–Mn Features | The specs for a set of features, usable end to end by a real user role | Milestone exit checklist below |
| Hardening | Performance, security and accessibility testing, runbook, handover | NFRs verified, runbook rehearsed, go-live checklist signed |

**Milestone exit checklist (G4):**

- all milestone specs merged and marked Done in `STATUS.md`;
- the E2E Playwright suite is green on staging, and the built screens match their approved S-xx, states included;
- the agent eval suite meets its thresholds over N runs;
- no open Severity 1 or 2 bugs;
- dashboards and alerts exist for the new flows;
- the client accepts the demo or UAT;
- release notes, `CHANGELOG.md` and a version tag are done;
- the retro is held and its actions recorded.

**Bug severity.** Bugs are tracked as issues linked to their `R-xx` and `SPEC-xx`:

- Sev 1: production down, data loss or a security breach. Fix immediately.
- Sev 2: a Must requirement broken with no workaround. Fix before milestone exit.
- Sev 3: broken, but a workaround exists. Schedule it.
- Sev 4: cosmetic. Fix when convenient.

## Build loop for each spec

Every spec goes through the same eight steps. Nothing reaches `main` without green CI, an AI review and a human approval.

&#91;embedded content: spec build loop · 6 steps, 2 checks\]

A red CI run, an unresolved review comment or a change request each send the spec back to Cursor on the same branch.

1. **Ready.** The spec meets the Definition of Ready:
   - `R-xx` linked and acceptance criteria written;
   - contract references, approved screens S-xx (for frontend specs) and test plan (`T-xx`) present;
   - dependencies merged;
   - the expected diff is under about 400 changed lines. A larger spec is split.
2. **Branch.** Create `feat/SPEC-xx-short-name` from the latest `main`, or `fix/`, `chore/` or `docs/` for other work. Merge it within about 1–3 days.
3. **Prompt.** Write the Cursor prompt from the template and save it at `plans/Mx/specs/SPEC-xx/prompt.md`, so the run can be repeated and reviewed.
4. **Implement.** Cursor (Composer 2.5) writes the code and the tests together, guided by AGENTS.md and the Cursor rules. The engineer reads the diff, runs the tests locally and iterates.
5. **Pull request.** Use a Conventional Commit title and fill the PR template with the spec, requirement, screen and test IDs.
6. **CI.** All required checks must pass (see CI/CD).
7. **Review.** Claude checks correctness against the spec and its screens, security and test gaps, and posts PR comments. The author resolves them, and a human reviewer or code owner approves.
8. **Merge.** Squash-merge to `main`; it deploys to dev automatically. Update the spec row in `STATUS.md` and delete the branch. When every spec for a screen has merged, mark the screen Built.

**Definition of Done for a spec:**

- acceptance criteria are covered by passing tests;
- make check passes locally, CI is green and the review is approved;
- contracts, ADRs and docs are updated where touched;
- new code paths emit traces and logs, and the rules are updated if a convention changed;
- `STATUS.md` is updated.

**AI tool hygiene.** Confirm at intake that the client allows AI-assisted development and which tools. Never put secrets, credentials or real client data into prompts, screens or fixtures; use synthetic data. Turn on Cursor's privacy mode where the client requires it.

## Testing model

Tests follow the pyramid: many fast tests on every PR, fewer cross-component tests nightly, and the full E2E and eval suites at each milestone. The tools listed are examples; pick yours in `TECH_STACK.md`.

| Level | Scope | Example tools | Runs | Gate |
| --- | --- | --- | --- | --- |
| Backend unit | Functions and services in isolation | pytest | Every PR | Must pass; coverage floor on changed code |
| Backend functional | API endpoints against a real database in a container | pytest, httpx, Testcontainers | Every PR | Must pass |
| Frontend unit and component | Components, hooks, state | Vitest, Testing Library | Every PR | Must pass |
| Contract | Backend ↔ frontend and backend ↔ agent tool schemas | OpenAPI validation, Pact | Every PR | No breaking change without a version bump |
| Integration (BE + FE) | Real backend and frontend with seeded data; screenshot checks of key screens against their S-xx | Playwright | Smoke on every PR, full suite nightly | Must pass |
| Agent, mocked | Agent logic with a stubbed model and recorded responses | pytest, fixtures | Every PR | Deterministic; must pass |
| Agent, live eval | Real model over a scenario set, N ≥ 10 runs | Eval runner | Nightly and per milestone | Pass rate at or above threshold; zero safety failures |
| E2E (BE + FE + agent) | Full user journeys including the agent | Playwright and the eval suite | Per milestone on staging, and nightly | Milestone exit gate |
| Non-functional | Load, security scanning, accessibility | k6, OWASP ZAP, axe | Hardening, and per milestone for key flows | NFR targets met |

Agent evals need their own discipline:

- versioned scenario sets with expected outcomes;
- graders that are rule-based where possible, with model-graded checks only where needed;
- tracked metrics: task success, tool-call correctness, safety violations, latency, cost;
- a red-team set for prompt injection;
- any regression against the last milestone blocks exit.

## CI/CD pipeline

One pipeline promotes the same build artifact from PR to dev, staging and production, with a gate at each step.

**Make and Docker.** Every task runs through one `Makefile`, and every service runs in a container through Docker Compose. Engineers, CI and Cursor use the same commands, so a green local run predicts a green PR.

| Target | Does |
| --- | --- |
| `make setup` | First-time setup: copy `.env.example` to `.env`, build the images, install git hooks |
| `make up`, `make down` | Start or stop the full local stack (services, database, any queues) |
| `make migrate`, `make seed` | Apply database migrations; load the synthetic fixtures |
| `make lint`, `make fmt` | Lint, type-check and format every service |
| `make test` | Unit, functional and component tests |
| `make test-int`, `make test-e2e` | Playwright integration and E2E runs against the running stack |
| `make eval` | Agent eval suite: mocked by default, live model with `LIVE=1` |
| `make check` | Everything the PR checks run; must pass before a PR is opened |

- CI jobs call these same targets rather than their own scripts.
- The host needs only Docker, make and git; no language toolchains installed locally.
- The same Dockerfiles build the images deployed to dev, staging and production.
- Secrets come from a git-ignored `.env` locally and from the vault elsewhere; `.env.example` is committed.

| Stage | Trigger | Checks | Blocks |
| --- | --- | --- | --- |
| PR checks | Every push to a PR | Lint, format, type check; every-PR tests from the testing model, including the Playwright smoke run; build and migration check; static analysis, dependency scan, secret scan | Merge |
| Main | Merge to `main` | Build the image, deploy to dev, smoke test | — |
| Nightly | Schedule | Full Playwright suite, live agent eval, dependency audit | Milestone sign-off while red |
| Release candidate | `vX.Y.0-rc` tag | Deploy to staging, E2E and eval suites, performance checks | Production promotion |
| Production | Approved release tag | Deploy behind feature flags, run migrations, smoke test, keep rollback ready | — |

**Practices:**

- branch protection on `main` through a ruleset: pull request required, squash merge only, linear history, conversations resolved, no force pushes or deletions, and the required checks once CI exists. Require at least one approval; a solo owner sets zero approvals and adds the repository admin to the bypass list "for pull requests only", so direct pushes stay blocked. Private repos need GitHub Pro or Team for rulesets to be enforced;
- GitHub flow with short-lived branches;
- feature flags for work that is merged but not yet released;
- SemVer tags and a `CHANGELOG.md` generated from Conventional Commits;
- infrastructure as code, and secrets in a vault, never in the repo;
- automated dependency updates (Renovate or Dependabot) and a licence check, each update merged through a normal PR;
- DORA metrics (deploy frequency, lead time, change failure rate, time to restore) reviewed at each retro.

## Observability

Observability is built in M0 and extended by every spec, so each new flow ships with its traces, logs, metrics and alerts.

- **Traces.** OpenTelemetry spans run across frontend → backend → agent → database, with one trace ID per user request.
- **Logs.** Structured JSON carrying the trace ID, request ID and tenant or user ID, with PII redacted.
- **Metrics.** Rate, errors and duration for every endpoint and job.
- **Agent telemetry.** Each run records:
  - model calls and tool calls;
  - tokens and cost;
  - latency;
  - model and prompt versions.

  Eval scores are kept over time.
- **SLOs.** Availability and latency targets per key journey, with alerts on error-budget burn rather than raw thresholds.
- **Per-spec rule.** A spec that adds a flow also adds its spans, log events and dashboard panel. This is part of the Definition of Done.

## Operate and support

Go-live starts the operate phase. It needs its own plan, written into `RUNBOOK.md` during hardening.

- **Hypercare.** A fixed period after go-live (often two to four weeks) with daily checks of errors, SLOs and agent evals, and fast fixes.
- **On-call and escalation.** Who responds, how they are reached, and the response time for each bug severity.
- **Incidents.** Each Sev 1 or Sev 2 incident gets a blameless postmortem in `docs/ops/incidents/` within a week, and its actions become specs or rules.
- **Backups and recovery.** Recovery point and recovery time targets come from the NFRs. A restore is rehearsed in hardening and on a schedule after that.
- **KPI review.** About 30 days after each release, compare the `KPI-xx` targets with the analytics, and feed the result into the retro and the next change requests.
- **Handover.** If another team will run the product, hand over the runbook, dashboards, access and a walkthrough before G5.

## Tracking and change control

`STATUS.md` is the one place to check progress. Every change to the PRD goes back through intake before it reaches the plan.

**`STATUS.md` holds:**

- the current milestone and next gate;
- the milestone table;
- the spec table for the current milestone, with each spec's screens, branch and PR, and the screen table (each S-xx with its requirements, specs and status);
- open questions and risks;
- recent ADRs.

Specs move through Draft → Ready → In progress → In review → Done, or Blocked with a reason. Screens move through Draft → Client review → Approved → Built.

Each week, send the client a short update generated from `STATUS.md`: what was done, what is next, risks, and decisions needed from them.

**Change control:**

1. Store the new PRD version or change request unchanged, as `CR-xx`.
2. Diff it against `REQUIREMENTS.md` and list the affected requirements, screens, ADRs, contracts, specs, tests and milestone dates.
3. The client approves the scope and date impact.
4. Update the owning docs downstream, add or change specs, and update `STATUS.md`.

No spec work starts on an unapproved change.

**Frozen and living docs:**

- `REQUIREMENTS.md`, `ARCHITECTURE.md`, `UI_DESIGN.md` and the approved screens are baselined at their gates and change only through change control.
- `STATUS.md`, ADRs, specs and the development plan are living docs.

## Repo layout

Every product repo uses the same layout, so the docs are always in the same place.

```
AGENTS.md         instructions every coding agent reads
CLAUDE.md         Claude review checklist, points to AGENTS.md
.cursor/rules/    000-core.mdc, backend.mdc, frontend.mdc, agent.mdc, ...
docs/
  PROCESS.md      this process, exported as Markdown
  sources/        PRD and client inputs, versioned; revised only by the product owner
  product/        REQUIREMENTS.md, QUESTIONS.md, UI_DESIGN.md
  design/         tokens.md, screens/S-01-<name>.html, ...
  discovery/      DISCOVERY.md (only if an existing system is involved)
  architecture/   ARCHITECTURE.md, TECH_STACK.md, SECURITY.md, OBSERVABILITY.md
  adr/            ADR-001-<slug>.md, ...
  contracts/      openapi.yaml, events/, agent-tools/
  ops/            RUNBOOK.md, RELEASE_NOTES.md, incidents/
plans/
  STATUS.md
  DEVELOPMENT_PLAN.md
  TEST_STRATEGY.md
  DELIVERY_PLAN.md
  M0/, M1/, ...   milestone.md and specs/SPEC-xx/{spec.md, prompt.md}
  retros/         M0.md, M1.md, ...
.github/          workflows/, pull_request_template.md, CODEOWNERS
Makefile          setup, up, down, test, lint, eval, check, ...
compose.yaml      local stack: every service plus database
docker/           one Dockerfile per service
.env.example      config keys with safe defaults; .env stays untracked
CHANGELOG.md
```

## Templates

Copy these into each new repo. The spec and the prompt are the two that matter most, because they drive every Cursor run.

**Spec** (`plans/Mx/specs/SPEC-xx/spec.md`)

```markdown
# SPEC-xx: <title>
Milestone: Mx | Status: Draft | Layer: backend / frontend / agent / cross-cutting
Requirements: R-xx, R-yy | Feature: F-xx | ADRs: ADR-xxx
Screens: S-xx (docs/design/screens/S-xx-<name>.html) | Branch: feat/SPEC-xx-<name>

## Goal
One sentence: what a user can do once this merges.

## Scope
In: ...
Out: ...

## Design
Components touched, contract references, data changes, migrations.

## Acceptance criteria
- AC1: Given ... when ... then ...

## Tests
- T-xx unit: ...
- T-xx functional / integration: ...
- T-xx E2E or eval scenario: ...

## Observability
Spans, log events and metrics added.

## Dependencies
Specs that must merge first; contract versions.
```

**Cursor prompt** (`plans/Mx/specs/SPEC-xx/prompt.md`)

```markdown
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
```

**ADR** (`docs/adr/ADR-xxx-<slug>.md`)

```markdown
# ADR-xxx: <decision>
Status: Proposed | Accepted | Superseded by ADR-yyy    Date: YYYY-MM-DD
Context: the forces and the R-xx / NFR-xx behind this choice.
Decision: what we chose.
Alternatives: what we considered and why we rejected each.
Consequences: what gets easier, what gets harder, what we must now do.
```

**Pull request** (`.github/pull_request_template.md`)

```markdown
## SPEC-xx: <title>
Requirements: R-xx | Screens: S-xx | Tests: T-xx
### What changed
### How it was tested
### Screenshots or traces
### Risk and rollback
- [ ] Acceptance criteria met
- [ ] Tests added or updated
- [ ] Contracts and docs updated
- [ ] STATUS.md updated
```

**Status** (`plans/STATUS.md`)

```markdown
# STATUS: <product>        Updated: YYYY-MM-DD
Current milestone: Mx | Next gate: <gate> on YYYY-MM-DD

| Milestone | Scope | Status | Exit date |
|---|---|---|---|

## Mx specs
| Spec | Requirements | Screens | Branch / PR | Status | Owner |
|---|---|---|---|---|---|

## Screens
| Screen | Requirements | Specs | Status |
|---|---|---|---|

## Open questions and risks
## Recent decisions
```

## What changed from the draft, and standards alignment

The draft's core shape is kept: PRD → design → plans → milestones of specs → branch, Cursor, PR, CI and Claude review → `STATUS.md`. The changes below close the gaps an industry-standard process would flag.

| Draft | Polished | Why |
| --- | --- | --- |
| PRD goes straight to architecture | Requirements intake and gate G1 come first | A client PRD has gaps. Catching them before design is cheapest, and it creates the IDs used for tracing |
| Decisions as a step after architecture | ADRs written during design | Decisions are made while designing; recording them later loses the reasons |
| One architecture and implementation plan | `ARCHITECTURE.md` (design) plus `DEVELOPMENT_PLAN.md` (specs and tasks) | Design changes slowly; the task plan changes weekly |
| Tech stack as its own step | Tool choices made as ADRs, summarised in `TECH_STACK.md` | Every tool keeps its reason |
| No contracts step | API, event and agent-tool schemas before work splits | Enables parallel work and contract tests |
| No security step | `SECURITY.md` threat model plus scans in CI | A baseline expectation, and more important with agents |
| Observability as a layer | Built in M0, extended by every spec | Adding tracing later is expensive |
| Ad hoc Cursor prompts | One saved prompt per spec, plus versioned AGENTS.md and Cursor rules | AI work becomes repeatable and reviewable, and conventions hold on every run |
| CI and Claude approve the merge | CI, then Claude review, then a human approval | A person stays accountable; AI review assists |
| Tests per layer | Plus when each runs (PR, nightly, milestone) and its threshold | Keeps PR checks fast and evals meaningful |
| `STATUS.md` only | Plus change control, milestone exit checklist and retros | Clients change scope, so the process needs a loop |

| Practice | Standard or reference |
| --- | --- |
| Lifecycle stages | ISO/IEC/IEEE 12207 |
| Requirements quality; NFR categories | ISO/IEC/IEEE 29148; ISO/IEC 25010 |
| Architecture description | C4 model, arc42, ISO/IEC/IEEE 42010 |
| Decision records | ADRs (Michael Nygard format) |
| Secure development | NIST SSDF (SP 800-218), OWASP ASVS, OWASP Top 10 for LLM Applications |
| AI risk | NIST AI Risk Management Framework |
| Branching, commits, versions | GitHub flow, Conventional Commits, Semantic Versioning |
| Delivery performance | DORA metrics |
| Observability | OpenTelemetry; SLOs and error budgets (Google SRE) |
| Ready and Done | Definition of Ready and Definition of Done (Scrum) |

## Running it in a Claude project

Set up once per product, then run one stage per thread. Generated docs live in the Git repo. The project holds only this process and the PRD.

**One-time setup**

1. Create an empty private GitHub repo for the product, set "Automatically delete head branches" and squash-only merging, and add the `main` ruleset (see CI/CD practices). Add required checks after M0 delivers CI.
2. In Claude, connect GitHub and install the Claude GitHub App on that repo, so threads can push branches and open PRs.
3. Export this doc as Markdown and name it `PROCESS.md`.
4. Create a Claude project. Attach the repo with push access, and upload `PROCESS.md` and the PRD as project files.
5. Paste the project instructions below, with the placeholders filled in.
6. Run the stage prompts below in order, each in a new thread. Review and merge each PR before starting the next stage.

If a thread cannot push, ask it for the files instead and commit them yourself.

**Project instructions** (paste into the project's custom instructions)

```text
Project: <Product name>. <One-sentence summary of what it does and for whom>.
Built from the client PRD using the process in PROCESS.md.

Where things are
- Process: PROCESS.md (project file). It defines the stages, gates, docs,
  IDs and templates. Follow it.
- PRD: <PRD file name> (project file), copied into docs/sources/. Edit it only
  when I say so, with a dated revision note, in both places.
- Repo: github.com/<owner>/<repo> (attached). The repo is the source of truth
  for every generated doc. Start every session from plans/STATUS.md.

Rules
- One stage per thread. Do only the stage asked for, stop at its gate,
  and list what I need to review or decide.
- Use the IDs from PROCESS.md (R-xx, NFR-xx, KPI-xx, F-xx, Q-xx, A-xx, ADR-xxx,
  S-xx, SPEC-xx, T-xx). Every requirement traces to a PRD section.
- Never invent requirements. A gap becomes a Q-xx with an assumption A-xx.
- One owner per fact: link to the owning doc instead of repeating it.
- Work on a branch named in the stage prompt and open a PR. Never push to main.
- Update plans/STATUS.md at the end of every stage.
- Ask me before choices that are expensive to reverse (cloud, database,
  model provider, auth). Decide the rest, record an ADR, and say which.

Stack: <known constraints, or "decided in stage 2">.

How I like to work: short replies, lead with the answer. When I say
"your call", pick a sensible default, say which, and continue.
```

**Stage prompts** (one thread each; replace the `<...>` parts)

**0. Bootstrap the repo**

```text
Set up the repo per the "Repo layout" in PROCESS.md. Copy the PRD into
docs/sources/ unchanged as PRD-v1.0.<ext>, and PROCESS.md into docs/.
Create every folder and doc as a stub with headings only. Create
plans/STATUS.md from the Status template (current: Stage 1, next gate: G1),
the PR template and CHANGELOG.md. Leave AGENTS.md and the Cursor rules for
Stage 3. Branch chore/bootstrap, open a PR, and summarise.
```

**1. Requirements intake**

```text
Run Stage 1 on docs/sources/<PRD file>.
- Product framing: confirm the PRD's personas, user journeys, user stories,
  and value and defensibility hypotheses; propose any that are missing in
  REQUIREMENTS.md and raise a Q-xx for each.
- docs/product/REQUIREMENTS.md: R-xx and NFR-xx, each with its PRD section,
  MoSCoW priority and Given/When/Then acceptance criteria; grouped into F-xx;
  an out-of-scope list; a coverage table (every PRD section -> R-xx or out
  of scope).
- docs/product/QUESTIONS.md: Q-xx, each with the assumption A-xx you would
  build on.
- DISCOVERY.md only if the PRD depends on an existing system.
Check Gate G1 and list what fails. Give me the open questions grouped by who
must answer them. Branch docs/stage-1-intake, PR, update STATUS.md.
```

After the client answers, in the same thread:

```text
Answers: <Q-xx: answer, ...>. Update REQUIREMENTS.md and QUESTIONS.md, mark
the questions resolved, and re-check G1.
```

**2. Design** (for a large PRD, split into 2a: architecture, ADRs and contracts; 2b: the rest)

```text
Run Stage 2 from docs/product/REQUIREMENTS.md, in the order PROCESS.md gives:
ARCHITECTURE.md (C4 levels 1-3 as Mermaid, data model, write path, a quality
scenario per NFR, an R-xx -> component table); an ADR for each significant
choice, written as you make it; docs/contracts/ (OpenAPI, event schemas,
agent tool schemas); UI_DESIGN.md (journeys and stories in scope, screens,
flows, states, an R-xx -> screen table); TECH_STACK.md (each tool linked to its ADR); SECURITY.md (STRIDE,
roles, data classification, agent risks); OBSERVABILITY.md (signals, SLO per
key journey). Check Gate G2 (screen approval comes in 2c) and list the gaps. Branch docs/stage-2-design,
PR, update STATUS.md.
```

**2c. Screens**

```text
Run the Screens step of Stage 2 from docs/product/UI_DESIGN.md. Put the shared
colours, type and spacing in docs/design/tokens.md. In Claude Design, make one
canvas: a journeys -> stories -> screens map, a "what it solves" page
(problems -> screens -> KPI-xx, moat hypotheses), and one page per journey
with its screens in step order, linked for click-through, each with a note
naming its journey step, stories, gate, R-xx, problem solved, moat built and
states to come. Give each screen an ID S-xx. Link the canvas from STATUS.md,
set the screens to Client review, and stop for my review on the canvas.
Branch design/screens-v1, PR.
```

After client feedback, in the same thread:

```text
Feedback: <S-xx: change, ...>. Update those screens on the canvas, and set the
approved ones to Approved in STATUS.md. Re-check Gate G2.
```

Once the canvas is approved, in the same thread:

```text
Build each approved screen as a self-contained HTML prototype matching the
canvas, with realistic synthetic data and its empty, loading and error states,
in docs/design/screens/S-xx-<name>.html. Link each from UI_DESIGN.md with its
journey step, stories and R-xx. Re-check Gate G2 on the same branch and PR.
```

**3. Plan and agent rules**

```text
Run Stage 3. Write DEVELOPMENT_PLAN.md (features -> SPEC-xx of about 1-3 days
each, dependency order, the S-xx each frontend spec builds, parallel tracks, branch naming, the Cursor and Claude
workflow), TEST_STRATEGY.md (levels, tools, what runs per PR / nightly /
milestone, eval thresholds, Definition of Done, pipeline and environments)
and DELIVERY_PLAN.md (M0, feature milestones as vertical slices with their
R-xx, hardening, RAID). Then write AGENTS.md, CLAUDE.md and
.cursor/rules/*.mdc per the Agent rules table, with frontmatter and ADR links.
Check Gate G3 and list the milestone scope I must agree with the client.
Branch docs/stage-3-plan, PR, update STATUS.md.
```

**4. Build: prepare a milestone** (then implement each spec in Cursor)

```text
Prepare milestone <Mx>: write plans/<Mx>/milestone.md and, for each of its
specs in DEVELOPMENT_PLAN.md, spec.md and prompt.md from the templates, with each frontend spec's S-xx
screens and its feat/SPEC-xx-<name> branch.
Check each spec against the Definition of Ready and order them by
dependency. Branch docs/<mx>-specs, PR, update STATUS.md.
```

For each spec: open its `prompt.md` in Cursor, run it with Composer 2.5 on `feat/SPEC-xx-<name>`, and open the PR. Then ask Claude:

```text
Review PR #<n> against plans/<Mx>/specs/<SPEC-xx>/spec.md, its S-xx screens, CLAUDE.md and the
spec Definition of Done. List blocking issues first, then suggestions.
Do not approve; I approve.
```

**5. Verify the milestone**

```text
Check milestone <Mx> against the exit checklist (G4), using STATUS.md, the
merged PRs and these results: <CI / E2E / eval links or pastes>. Mark each
item pass or fail with evidence, list open bugs by severity, and draft the
UAT script from the acceptance criteria of the milestone's R-xx.
```

**6. Release**

```text
Prepare release <vX.Y.0> for <Mx>: a RELEASE_NOTES.md entry in client
language, mapped to R-xx; CHANGELOG.md from the merged Conventional Commits;
RUNBOOK.md updates for the new flows (deploy, rollback, alerts, common
failures). Report the go-live checklist (G5). Branch docs/release-<vX.Y.0>, PR.
```

**7. Learn and change**

```text
Retro: write plans/retros/<Mx>.md from STATUS.md, the PR history and my
notes: <notes>. Cover what worked, what didn't, and actions with owners.
List proposed changes to PROCESS.md, the rules or the templates separately.
```

```text
Change request: the client sent <CR-xx / PRD v1.1>, now in docs/sources/.
Run change control: diff it against REQUIREMENTS.md, list the affected R-xx,
ADRs, contracts, screens, specs, tests and milestone dates, and estimate the impact.
Change no doc until I confirm.
```

## Quick start with a new PRD

Follow these eight steps to take a new PRD through the process for the first time.

1. Create an empty private GitHub repo for the product, set "Automatically delete head branches" and squash-only merging, and add the `main` ruleset (see CI/CD practices). Add required checks after M0 delivers CI.
2. In Claude, connect GitHub and install the Claude GitHub App on that repo, so threads can push branches and open PRs.
3. Export this doc as Markdown and save it as `PROCESS.md`.
4. Create a new Claude project. Attach the repo with push access, and upload `PROCESS.md` and the PRD as project files.
5. Paste the project instructions from the previous section, and fill in the product name, summary, PRD file name and repo.
6. In a new thread, run prompt 0 to bootstrap the repo, then merge its PR.
7. In another new thread, run prompt 1 for requirements intake. Review the requirements list and the open questions, get the questions answered, and send the follow-up prompt.
8. Run stage 2, then the screens prompts (2c: canvas, your review, then HTML), then stage 3, one thread each. Merge each PR before starting the next stage. Cursor starts only at stage 4, once the specs and rules exist.

On a first run, stages 1–3 show where the process or prompts need adjusting. Note those changes and fold them back into this doc after M0.
