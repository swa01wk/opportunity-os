# Contracts

Agreed in Stage 2a, before backend, web, agent and media work splits. Contract version **0.2.0** (draft until the M0 contracts spec regenerates these files from Pydantic, ADR-008; then 1.0.0). Never changed outside a spec. Architecture context: [ARCHITECTURE.md](../architecture/ARCHITECTURE.md).

| Contract | Files | Producer → consumer | Requirements |
|---|---|---|---|
| Studio API | [openapi.yaml](openapi.yaml) | api → web | R-01–R-63 (R1–R2 scope) |
| Common types | [common.schema.json](common.schema.json) | all | NFR-19 |
| Domain events | [events/domain-event.schema.json](events/domain-event.schema.json) | api, worker → relay, web (SSE), audit | R-41, R-44, R-50, NFR-09 |
| Workflow requests | [events/workflow-request.schema.json](events/workflow-request.schema.json) | api → worker dispatcher | NFR-01, ADR-003 |
| Agent tasks | [agent-tools/tasks.json](agent-tools/tasks.json), [task-io.schema.json](agent-tools/task-io.schema.json) | worker ↔ agent | R-08, R-14, R-16, R-63 |
| Agent tools | [agent-tools/tools.schema.json](agent-tools/tools.schema.json) | model → agent tool host (read-only) | R-43, NFR-05 |
| Scene spec | [media/video-spec.schema.json](media/video-spec.schema.json) | agent, web → render | R-18–R-22, NFR-05 |
| Capability catalogue | [media/capabilities.json](media/capabilities.json) | render, demonstrations → agent, api preflight | R-07, R-19 |
| Demonstration model | [media/demonstration.schema.json](media/demonstration.schema.json) | worker → render, web | R-11–R-13 |
| Narration timing, captions | [media/timing.schema.json](media/timing.schema.json) | worker (media/audio) → render | R-25–R-27 |
| Render job | [media/render-job.schema.json](media/render-job.schema.json) | worker ↔ render (private network) | R-28, R-29, NFR-12 |
| Render manifest | [media/render-manifest.schema.json](media/render-manifest.schema.json) | render → api, web, export | R-30, R-32, NFR-03 |
| KPI analytics events | [analytics/events.schema.json](analytics/events.schema.json) | outbox relay → `analytics.event` → Grafana views | KPI-01–KPI-14, ADR-017 |
| Database draft | [db/schema.sql](db/schema.sql) | backend migrations (Alembic) | R-41, R-34, PRD §15 |
| Fixtures | [examples/](examples/), [examples/invalid/](examples/invalid/) | CI in both runtimes | NFR-19, QA-01, QA-02 |

## Mocking across layers

- **web** mocks the API from `openapi.yaml` and drives the Remotion Player with `examples/odd-squares.video-spec.json`.
- **agent** runs against fake `LlmProvider` responses and the tool schemas; `validate_scene_spec` can be stubbed with the invalid-fixture manifest.
- **media** renders `examples/odd-squares.video-spec.json` with a synthetic timing file; needs no API.
- **backend** fakes the render service with `RenderJobStatus` fixtures and the agent with stored task outputs.

## Validation levels

1. **Schema** (JSON Schema 2020-12 / Pydantic / Ajv): shape, enums, bounds, IDs. Fixtures with `level: schema` in [examples/invalid/manifest.json](examples/invalid/manifest.json) must fail here.
2. **Semantic** (compiler, in `render` with a Python mirror for preflight). Must fail with the listed `ValidationError.code`:

| Rule | Code | Requirement |
|---|---|---|
| Every target, anchor, group, claim, asset and segment reference resolves; IDs unique | `UNKNOWN_REFERENCE`, `DUPLICATE_ID` | R-18 |
| `startFrame < endFrame ≤ scene.durationFrames`; scenes sum to `targetDurationFrames`; 900–2700 frames | `FRAME_OUT_OF_RANGE`, `DURATION_OUT_OF_RANGE` | R-21, NFR-16 |
| Op and params are in `capabilities.json`; object and action counts within limits | `CAPABILITY_UNSUPPORTED`, `PARAM_OUT_OF_BOUNDS`, `TOO_MANY_OBJECTS` | R-07, R-19, NFR-12 |
| Every `valueRef` equals the demonstration result; group cell counts match; params inside the function domain | `DEMONSTRATION_MISMATCH`, `DOMAIN_ERROR` | R-11, R-12 |
| Scene entry state equals the computed exit state of the previous scene | `CONTINUITY_BREAK` | R-22 |
| A term's colour equals the colour of the objects it is linked to; colour never carries meaning alone (label, group or position present) | `COLOR_MEANING_CHANGED`, `COLOR_ONLY_MEANING` | R-20 |
| Text and captions inside brand safe zones; captions never overlap an active object, label or equation; labels fit | `SAFE_ZONE`, `CAPTION_OVERLAP`, `LABEL_OVERFLOW` | R-23, R-27 |
| Assets licensed and not expired | `ASSET_UNLICENSED`, `ASSET_EXPIRED` | R-55 |
| Masters need `timing.status = measured` and resolved phrase anchors | `TIMING_NOT_MEASURED`, `ANCHOR_UNRESOLVED` | R-26 |

3. **Authority** (API): version-bound approvals, blockers and responsibilities. Not expressible in schema; tested as QA-05 (Stage 3, TEST_STRATEGY.md).

## Versioning

- Each schema has `$id` (a non-resolvable `opportunityos.invalid` URL) and `x-version`. VideoSpec and RenderManifest also carry the version in the document (`schemaVersion`, `manifestVersion`), because stored specs outlive code.
- Additive optional fields: minor bump. Removing or tightening anything: major bump, a migration for stored documents and a spec that names the change (PROCESS contract rule).
- `openapi.yaml` `info.version` follows the same rule; the API path prefix `/v1` changes only on a breaking change to the whole API.
- R3 additions (connections, connected publishing, experiments, opportunity lab) are a minor version added by the spec that starts R3 (A-18).

## Change log

| Version | Stage | Changes |
|---|---|---|
| 0.1.0 | 2a | First agreed contracts. |
| 0.2.0 | 2b | Additive. `DELETE /projects/{id}` (never-published projects only; published → 409 with `archive` option) and `archived` on projects (NFR-10 AC2). `GET/POST /kpi-baselines` and `app.kpi_baseline` (KPI-04, Q-13). `analytics` schema, `analytics.event` and `analytics/events.schema.json` (ADR-017). Domain events `project.archived`, `project.deletion_requested`, `project.deleted`, `kpi.baseline_recorded`; workflow type `project_deletion`. `fetch_source` limited to search results, operator URLs and one-hop links from fetched pages, with a new `links` output and `maxLinkHops` budget (SECURITY TH-14). Step-up sign-in rule documented in `openapi.yaml`. |
