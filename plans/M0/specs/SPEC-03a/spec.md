# SPEC-03a: Contracts I: Pydantic pipeline, drift and dual-runtime fixtures, common types and workflow requests
Milestone: M0 | Status: Draft (ready when SPEC-01a merges) | Layer: cross-cutting
Agent (if any): —
Requirements: NFR-19, NFR-11 | Feature: F-06 (contract foundation) | ADRs: ADR-008, ADR-003, ADR-019
Screens: — | Branch: `feat/SPEC-03a-contracts-pipeline`

## Goal
`make contracts` generates JSON Schema and TypeScript types from canonical Pydantic models, CI fails on any drift, and every fixture passes or fails identically in Pydantic and Ajv, starting with the common types and the workflow request.

## Scope
In:
- `contracts/python/opportunityos_contracts/` package: `common.py` (every `$def` in `common.schema.json`) and `events/workflow_request.py`.
- Generator `contracts/python/opportunityos_contracts/_build.py` behind `make contracts`: writes `docs/contracts/**/*.schema.json` (2020-12, keeping `$id` and `x-version`) and `contracts/ts/` via `json-schema-to-typescript`. Deterministic output (sorted keys, stable formatting).
- Equivalence check: for each regenerated file, a test normalises the generated schema and the hand-written 0.4.0 file and asserts they match (properties, required, enums, bounds, patterns, `additionalProperties`), except the additions this spec lists.
- Dual-runtime fixture harness in `contracts/tests/`: runs every file in `docs/contracts/examples/` and `examples/invalid/manifest.json` (schema level) through Pydantic and Ajv and asserts the same verdict (NFR-19). Later parts register their schemas with it.
- Drift check target `make contracts-check` (regenerate, `git diff --exit-code`), called by the `contracts` CI job.
- Contract addition (A-43): `workflowType` gains `diagnostic`.

Out: events, AG-UI and analytics (SPEC-03b); agent contracts (SPEC-03c); media (SPEC-03d); OpenAPI and the 1.0.0 cut (SPEC-03e).

## Design
- Rules: [contracts.mdc](../../../../.cursor/rules/contracts.mdc) (Pydantic canonical, never hand-edit generated files, schema style).
- Version: files keep `x-version` until SPEC-03e cuts 1.0.0; the change-log row "1.0.0 (in progress)" is opened here and completed by SPEC-03e.
- After this merges, the regenerated files are generated: hand edits fail CI (AGENTS.md Never).
- Expected diff: about 400 hand-written lines; generated JSON Schema and TS excluded.

## Acceptance criteria
- AC1 (NFR-19): Given the Pydantic models, when `make contracts` runs twice, then the second run changes no file.
- AC2 (NFR-19): Given a hand edit to a generated schema or TS file, when `make contracts-check` runs, then it fails and names the file.
- AC3: Given `common.schema.json` and `workflow-request.schema.json` 0.4.0, when compared with the generated files, then they are equivalent except for the `diagnostic` workflow type.
- AC4 (NFR-19): Given every valid example and every schema-level invalid fixture that uses these schemas, when run through Pydantic and Ajv, then both give the same verdict, and invalid fixtures fail with the code in `manifest.json`.
- AC5 (NFR-11): Given the generated TS types, when `contracts/ts` builds, then `tsc --noEmit` passes and the package exports one type per `$def`.

## Tests
- T-33 contract: codegen idempotence and drift (AC1, AC2), 0.4.0 equivalence (AC3), dual-runtime fixture verdicts (AC4), TS build (AC5), in `contracts/tests/`.

## Observability
None at runtime. The `contracts` CI job prints which schemas drifted.

## Dependencies
SPEC-01a. A-43 (accepted 14 Nov 2026) sets the diagnostic workflow type. Contracts: from 0.4.0. Size M (2 spec-days).
