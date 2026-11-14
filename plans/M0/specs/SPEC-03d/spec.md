# SPEC-03d: Contracts IV: media contracts (VideoSpec, capabilities, demonstration, timing, render job, manifest) in Pydantic
Milestone: M0 | Status: Draft (ready when SPEC-03a merges) | Layer: cross-cutting
Agent (if any): —
Requirements: NFR-19, R-18 | Feature: F-06 | ADRs: ADR-008, ADR-002
Screens: — | Branch: `feat/SPEC-03d-contracts-media`

## Goal
The render service, the compiler and the worker code against generated media types, and the odd-squares and invalid VideoSpec fixtures give the same schema verdict in Python and TypeScript.

## Scope
In:
- Pydantic models for `media/video-spec`, `demonstration`, `timing`, `render-job` and `render-manifest` schemas; a model for `capabilities.json`, validated as data.
- Register the odd-squares VideoSpec and demonstration fixtures and every `examples/invalid/` entry with `level: schema` in the fixture harness. Semantic-level fixtures stay for the compiler (SPEC-16).
- `schemaVersion` and `manifestVersion` stay inside documents (contracts README, Versioning).

Out: compiler rules (SPEC-16, SPEC-17); render behaviour (SPEC-12).

## Design
Same rules and equivalence check as SPEC-03a. Discriminated unions for actions and objects; no `if/then` (contracts.mdc). Expected diff: about 380 hand-written lines.

## Acceptance criteria
- AC1 (NFR-19): Given the six 0.4.0 media files, when compared with the generated ones, then they are equivalent.
- AC2 (R-18, NFR-19): Given `odd-squares.video-spec.json`, when validated, then it passes in both runtimes; given each schema-level invalid VideoSpec fixture, then both runtimes reject it with the expected code.
- AC3: Given a float where an integer frame is required, when validated, then both runtimes reject it (`float-value` fixture).

## Tests
- T-33 contract: equivalence and fixture verdicts for the media schemas (AC1–AC3).

## Observability
None at runtime.

## Dependencies
SPEC-03a. Contracts: from 0.4.0. Size S (1 spec-day).
