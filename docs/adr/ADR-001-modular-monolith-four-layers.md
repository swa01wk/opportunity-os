# ADR-001: Modular monolith in four layers, with a separate render worker
Status: Accepted    Date: 2026-11-12

## Context
PRD §14 asks for "a modular application with separately executable media workers", and §14.2 rules out microservice fleets and Kubernetes for launch (project hard limit). Rendering needs Node and a headless Chrome (ADR-002), while content, agent tasks and integrations are Python (PRD §14.2). Requirements: R-61, R-63, NFR-12, NFR-13.

## Decision
One repository, four code layers, five runtime containers:

| Layer | Code | Runs in |
|---|---|---|
| backend | `backend/` Python: API, domain, workflows, adapters | `api` (FastAPI) and `worker` (durable workflows) |
| agent | `agent/` Python package: research, script and storyboard tasks, LLM adapter, evals | imported by `worker` only |
| media | `media/scenes/` TypeScript: scene library, compiler, render service · `media/audio/` Python: TTS adapter, alignment, captions | `render` (Node, Remotion) · `media/audio` imported by `worker` |
| web | `web/` TypeScript: Next.js Studio | `web` |

Plus PostgreSQL and S3-compatible storage. `api` and `worker` are the same Python codebase started with different entry points. Layers talk only through the contracts in `docs/contracts/`.

## Alternatives
- **Single Python process doing everything:** cannot host Remotion (Node + Chrome) and would let a render crash take down the API.
- **One service per PRD §14.1 responsibility:** a microservice fleet, explicitly out of scope.
- **Render inside the Next.js server:** couples Studio uptime to multi-minute CPU-heavy renders and breaks resource isolation (NFR-12).

## Consequences
- Easier: one deploy pipeline, one database, shared contracts, local stack is one `make up`.
- Harder: two languages; contracts must be generated, not hand-copied (ADR-008).
- Must do: Cursor rules per layer (`backend.mdc`, `agent.mdc`, `media.mdc`, `frontend.mdc`) in Stage 3; render worker gets CPU/memory/time limits (NFR-12).
