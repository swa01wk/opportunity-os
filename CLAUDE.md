# CLAUDE.md

Conventions for this repo are in [AGENTS.md](AGENTS.md) and `.cursor/rules/*.mdc`; Claude and Cursor follow the same ones. This file adds the **PR review checklist** and how Claude works on stage tasks.

## Working in this repo (stage work)

- Start from [plans/STATUS.md](plans/STATUS.md). Follow the stage prompt in [docs/PROCESS.md](docs/PROCESS.md): one stage per thread, stop at its gate, list what the owner must review or decide.
- Work on the branch the stage names and open a PR. Never push to `main`. Update STATUS.md at the end of every stage.
- Never invent requirements: a gap becomes a Q-xx with an assumption A-xx in `docs/product/QUESTIONS.md`.
- Ask the owner before choices that are expensive to reverse (cloud, database, model or TTS provider, auth, Remotion licence). Decide the rest, record an ADR and say which.
- Never edit `docs/sources/PRD-v2.0.md`.

## PR review

Prompt: "Review PR #n against plans/Mx/specs/SPEC-xx/spec.md, its S-xx screens, CLAUDE.md and the spec Definition of Done. List blocking issues first, then suggestions. Do not approve; I approve."

Read the spec, its prompt, the contracts and ADRs it names, the rule files for the layers it touches and, for frontend specs, the screen prototype and its UI_DESIGN row. Then check the diff and the CI results.

**Output.** Blocking issues first, then suggestions, then questions. Each item: file and line, what is wrong, why (rule, ADR or R-xx), and the fix. Post as PR comments. Never approve or merge; the owner does.

### Blocking if any of these fail

**Spec and scope**
- [ ] Every acceptance criterion in the spec is implemented and covered by a test; refusal and blocked cases included.
- [ ] Only the paths the prompt allows changed; no unrequested features; diff about 400 lines or less, or the spec was split.
- [ ] Every T-xx the spec lists exists, is named with its ID and passes; new T-xx are added to the TEST_STRATEGY.md catalogue.

**Authority and safety** (AGENTS.md three truths)
- [ ] No path lets an agent or service identity approve, publish, raise budget or change a gate (R-43); member and responsibility are checked in the API per the SECURITY.md matrix (R-05).
- [ ] Consequential commands follow the write path: `If-Match`, `Idempotency-Key`, one transaction with audit row and outbox event; authority, cancellation and budget re-checked in the step transaction before the effect (backend.mdc).
- [ ] Approvals bind to the exact version hash and policy versions; a changed target invalidates them (R-41, R-42).
- [ ] Nothing executes model output, fetched content or a spec (`eval`, `exec`, `new Function`, `subprocess`, dynamic import, string-built SQL, `dangerouslySetInnerHTML`).
- [ ] Untrusted text is delimited as data in prompts; tools stay read-only and allowlisted; agent results pass schema → freshness → acceptance before storage (agent.mdc).
- [ ] Every query is workspace-scoped; RLS not bypassed; media only through short-lived signed URLs (NFR-04).
- [ ] No secrets, tokens, real channel or personal data in code, fixtures, prompts, logs or screens; new config keys are in `.env.example`.

**Contracts and data**
- [ ] Contract changes are named in the spec, made first, regenerated with `make contracts` (no hand edits to generated files), version-bumped with a change-log line, with fixtures for both runtimes (contracts.mdc).
- [ ] Migrations have a working downgrade; populated tables use expand → migrate → contract.
- [ ] Content versions are insert-only with SHA-256; masters are immutable; money in minor units; times in UTC.

**Reliability**
- [ ] DBOS workflow code is deterministic; steps are idempotent by attempt ID or input hash; retries stop at the ceiling; external uncertainty is recorded, never assumed successful (NFR-01).
- [ ] Budget is reserved before dispatch and settled after; no path can overspend (NFR-07).

**Media** (for `media/**`)
- [ ] Values come from `valueRef` only; compiler errors use the contract codes and name scene, object and field; house style only from brand-kit tokens; measured timing for masters; no silent speed-up; render limits enforced (media.mdc).

**Studio** (for `web/**`)
- [ ] The screen matches its approved prototype's layout, copy and every listed state, rebuilt with our components and tokens, not copied HTML.
- [ ] Commands are REST with version hashes; the AG-UI stream is observe-only with snapshot, dedupe and gap handling.
- [ ] Honest states: unavailable is not empty or zero; exported is not published; problem responses map as UI_DESIGN.md says.
- [ ] Keyboard path, focus handling, labels, status not by colour alone; axe clean (WCAG 2.2 AA).

**Observability**
- [ ] New flows emit their spans, named log events and metrics with correlation attributes, add a dashboard panel, and update OBSERVABILITY.md; nothing sensitive is logged (observability.mdc).

**Done**
- [ ] CI is green; diff coverage floors met; docs, ADRs and rules touched by the change are updated; STATUS.md is updated.

### Suggestions (non-blocking)

Naming, simpler structure, missing edge-case tests beyond the acceptance criteria, clearer error copy, duplicated code that an existing component or helper already covers.

### When a mistake repeats

If the same issue appears in two reviews, propose the rule change (which `.mdc` file, what line) so it is fixed in that PR.
