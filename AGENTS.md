# AGENTS.md

Instructions every coding agent (Cursor, Claude) follows in this repo. Layer-specific rules are in `.cursor/rules/*.mdc` and load only where they apply. The Claude review checklist is in [CLAUDE.md](CLAUDE.md).

## The product

OpportunityOS is an internal studio that turns a viewer question into an original, narrated 9:16 animated explainer (maths, science, technology) with claim evidence, human review gates, version-bound approval and honest publication records. One operator (the owner) uses it at R1–R2, on a local Docker Compose stack.

Three things are true everywhere in the code:

1. **Agents prepare drafts; people approve.** The research, script and storyboard agents write draft versions. Only a signed-in member records an approval or a public action (R-43). Model output never changes protected state on its own.
2. **Nothing generated is executed.** Model output, fetched pages and assets are untrusted data. Videos are built from a typed VideoSpec mapped to reviewed components (NFR-05).
3. **Every consequential change is versioned, bound and recorded.** Immutable versions with SHA-256 hashes, approvals bound to the exact hash, an audit row and an outbox event in the same transaction.

## Start here

- Where things stand: [plans/STATUS.md](plans/STATUS.md).
- The spec you are implementing: `plans/Mx/specs/SPEC-xx/spec.md`, and its Cursor prompt `prompt.md` next to it.
- Spec order, branches and the build loop: [plans/DEVELOPMENT_PLAN.md](plans/DEVELOPMENT_PLAN.md).
- Test levels, T-xx catalogue, Definition of Done: [plans/TEST_STRATEGY.md](plans/TEST_STRATEGY.md).
- Process (stages, gates, templates): [docs/PROCESS.md](docs/PROCESS.md).

## Repo map

Docs exist now; the code folders are created by SPEC-01 (M0). If SPEC-01 changes a path, it updates this map in the same PR.

```
AGENTS.md, CLAUDE.md        agent instructions and review checklist
.cursor/rules/              000-core, backend, agent, media, frontend, contracts, testing, observability
docs/
  sources/PRD-v2.0.md       the PRD (never edit)
  product/                  REQUIREMENTS.md (R-xx, NFR-xx, KPI-xx), QUESTIONS.md (Q-xx, A-xx), UI_DESIGN.md (S-xx)
  architecture/             ARCHITECTURE.md, AGENT_ARCHITECTURE.md, TECH_STACK.md, SECURITY.md, OBSERVABILITY.md
  adr/                      ADR-001 … ADR-022
  contracts/                openapi.yaml, events/, agent-tools/, agui/, media/, analytics/, db/schema.sql, examples/
  design/                   tokens.md, screens/S-xx-<name>.html (approved prototypes)
  ops/                      RUNBOOK.md, RELEASE_NOTES.md, incidents/
plans/                      STATUS.md, DEVELOPMENT_PLAN.md, TEST_STRATEGY.md, DELIVERY_PLAN.md, Mx/specs/, retros/
backend/                    Python: api (FastAPI) and worker (DBOS) entry points, one package
  opportunityos/api/        routers (thin), dependencies, problem responses
  opportunityos/domain/     aggregates, state machine, guards, services
  opportunityos/repo/       SQLAlchemy repositories, workspace-scoped
  opportunityos/workflows/  DBOS workflows and steps, dispatcher, outbox relay, AG-UI projection
  opportunityos/adapters/   ports, implementations and fakes (identity, blob, fetch, search)
  migrations/               Alembic
  tests/                    unit/, functional/, conformance/
agent/                      Python package imported by the worker only
  opportunityos_agent/      runner/, tasks/{research,script,storyboard}/, tools/, llm/
  prompts/<task>.md         versioned prompts
  evals/<task>/             eval scenarios, golden outputs, red team; evals/holdout/
  tests/
media/
  scenes/                   TypeScript: families, components, compiler, render service, media QA, tokens
  audio/                    Python: TTS adapters, alignment, caption segmentation
web/                        Next.js Studio: app/, components/, lib/, tests/
contracts/
  python/opportunityos_contracts/   canonical Pydantic models (ADR-008)
  ts/                               generated TypeScript types (never hand-edit)
e2e/                        Playwright: smoke/, screens/ (T-15–T-30), journeys/, conformance/, nfr/
docker/                     one Dockerfile per service
infra/                      Compose-adjacent config: otel collector, grafana provisioning, keycloak realm (no secrets), drills
releases/                   release records (commit, image digests), ADR-022
Makefile, compose.yaml, .env.example, CHANGELOG.md
```

Layers (ADR-001) talk only through the contracts in `docs/contracts/`. `agent/` is imported only by the worker; `media/scenes` is imported by `web` for the Remotion Player and runs as the `render` service; `media/audio` is imported by the worker.

## Commands

Everything runs through `make` inside containers; the host needs only Docker, make and git (PROCESS.md, ADR-019). The targets are stubs until SPEC-01 implements them.

| Target | Does |
|---|---|
| `make setup` | First run: copy `.env.example` to `.env`, build images, install git hooks (gitleaks) |
| `make up`, `make down` | Start or stop the local stack (`oos-dev`) |
| `make migrate`, `make seed` | Apply migrations; load synthetic fixtures |
| `make contracts` | Regenerate JSON Schema and TS types from the Pydantic models |
| `make lint`, `make fmt` | Lint, type-check, format every layer |
| `make test` | Unit, functional, component, contract and mocked agent tests |
| `make test-int`, `make test-e2e` | Playwright integration and E2E against the running stack |
| `make eval` | Agent evals, fake model by default; `LIVE=1` for the real model |
| `make check` | Everything the PR checks run. Must pass before opening a PR |
| `make r0-sample` | The R0 odd-squares pipeline (SPEC-25) |
| `make release`, `make deploy ENV=…`, `make promote` | Build once, deploy to staging, promote by digest (ADR-022) |

## Working on a spec

1. Read the spec, its prompt, the contracts and ADRs it names, and for frontend work its screen in `docs/design/screens/` and `docs/design/tokens.md`.
2. Change only the paths the spec allows. Do not change a public contract unless the spec says so.
3. Write the tests listed under "Tests" first (named with their T-xx), make them pass, run `make check`.
4. Report: what changed, tests added, any deviation from the spec and why, any new dependency.

If the spec is wrong, ambiguous or would need more than about 400 changed lines, stop and say so instead of guessing.

## Never

- Never execute model output, fetched content or anything derived from it (`eval`, `exec`, `new Function`, `subprocess`, dynamic imports, SQL built from it).
- Never let an agent or service identity record an approval, publish, raise a budget or change a gate.
- Never hand-edit generated files (`docs/contracts/**/*.schema.json` after SPEC-03, `contracts/ts/`).
- Never change a contract, migration or prompt outside a spec that names it.
- Never put secrets, tokens, real channel data or personal data in code, fixtures, prompts, screens, logs or commits. Synthetic data only (A-23).
- Never scrape or automate a browser in place of a missing platform API (NFR-18).
- Never weaken or delete a test, eval or threshold to make a change pass.
- Never push to `main`; never force-push a shared branch.
- Never edit `docs/sources/PRD-v2.0.md`.
