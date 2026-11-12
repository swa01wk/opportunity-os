# ADR-008: Pydantic is the canonical schema; JSON Schema and TypeScript types are generated
Status: Accepted    Date: 2026-11-12

## Context
The same contracts (VideoSpec, timing, manifests, events, task outputs, API bodies) are used by Python (api, worker, agent, audio) and TypeScript (web, render). NFR-19 requires one canonical source and shared valid/invalid fixtures passing in both runtimes.

## Decision
- From M0, Pydantic v2 models in `contracts/python/opportunityos_contracts/` are the source of truth.
- `make contracts` generates:
  - JSON Schema (draft 2020-12) into `docs/contracts/**/*.schema.json`;
  - TypeScript types into `contracts/ts/` (via `json-schema-to-typescript`), imported by `web/` and `media/scenes/`;
  - the TypeScript runtime validator uses Ajv on the same JSON Schema files.
- Fixtures in `docs/contracts/examples/` (valid) and `docs/contracts/examples/invalid/` run through Pydantic and Ajv in CI; any disagreement fails the build.
- **Stage 2a bootstrap:** the JSON Schemas in `docs/contracts/` are hand-written now as the agreed contract. The first M0 contracts spec writes Pydantic models that regenerate them; CI then forbids hand edits.
- Every schema carries `$id` with a semantic version. A breaking change bumps the major version and is made only inside a spec (PROCESS contract rule).

## Alternatives
- **JSON Schema hand-maintained as the source, Pydantic generated:** code generation into Pydantic is weaker for validators and computed fields.
- **TypeScript (Zod) as the source:** puts the canonical model away from the domain and agent code.
- **Protobuf:** no gain for JSON-over-HTTP and jsonb storage; poorer optional/union handling.

## Consequences
- Easier: no hand-copied types; contract drift is a CI failure.
- Harder: some JSON Schema features (conditional `if/then`) need care in both generators; keep schemas to discriminated unions and simple bounds.
