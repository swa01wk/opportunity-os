# SPEC-03b: Contracts II: domain events, AG-UI stream and analytics events in Pydantic
Milestone: M0 | Status: Draft (ready when SPEC-03a merges) | Layer: cross-cutting
Agent (if any): —
Requirements: NFR-19, R-50 | Feature: F-14 (event contracts) | ADRs: ADR-008, ADR-010, ADR-017, ADR-020
Screens: — | Branch: `feat/SPEC-03b-contracts-events`

## Goal
Domain events, the AG-UI project stream definitions and the KPI analytics events are generated from Pydantic, so the relay and the Studio code against generated types.

## Scope
In:
- Pydantic models for `events/domain-event.schema.json`, the `$defs` of `agui/stream.json` (its `x-agui` mapping block stays data and is validated against a model) and `analytics/events.schema.json`; regenerated through `make contracts`.
- Contract additions (A-43): `StepName` accepts `diagnostic.echo`, `diagnostic.validate` and `diagnostic.join`; a recorded example `examples/agui/diagnostic-run.stream.jsonl` (snapshot, run started, three steps, run finished, ordered `seq`).
- Register these schemas and the four existing recorded streams with the SPEC-03a fixture harness (every frame's payload validates; cursors strictly increase).

Out: AG-UI SDK field check against the pinned SDK (SPEC-10); relay code (SPEC-09a, SPEC-10).

## Design
- Same rules and equivalence check as SPEC-03a. Events carry references and redacted summaries only (contracts.mdc).
- Expected diff: about 350 hand-written lines.

## Acceptance criteria
- AC1 (NFR-19): Given the three 0.4.0 files, when compared with the generated ones, then they are equivalent except for the diagnostic step names.
- AC2: Given each recorded stream in `examples/agui/`, including the new diagnostic stream, when validated, then every payload passes in Pydantic and Ajv and `seq` strictly increases.
- AC3: Given an event payload with an unknown property, when validated, then both runtimes reject it (`additionalProperties: false`).

## Tests
- T-33 contract: equivalence, recorded-stream validation and rejection cases for these schemas (AC1–AC3).

## Observability
None at runtime.

## Dependencies
SPEC-03a. Contracts: from 0.4.0. Size S (1 spec-day).
