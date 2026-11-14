# SPEC-12: Render service skeleton, job API and resource limits
Milestone: M0 | Status: Draft (ready when SPEC-03d and SPEC-05 merge) | Layer: media
Agent (if any): —
Requirements: R-29, NFR-12 | Feature: F-08 | ADRs: ADR-002, ADR-007, ADR-003
Screens: — | Branch: `feat/SPEC-12-render-skeleton`

## Goal
The worker can submit a render job to a private render service that is idempotent by input hash, validates the VideoSpec it is given, and fails cleanly when a job breaks its CPU, memory, time or size limits.

## Scope
In:
- `media/scenes/render/` Node service on the private network: `POST /jobs` (validates `RenderJobRequest` with Ajv against the generated schema), `GET /jobs/{jobId}`. `jobId` is the effective input hash; a repeated request returns the existing job.
- Job store in `media.render_job` (role `oos_render`) with a lease (`leased_until`) so a crashed job becomes claimable again; `attempts` counted.
- Kinds at M0: `validate` reads the VideoSpec by `BlobRef` from the object store (render credential, SPEC-05) and runs schema validation; `scene_clip`, `preview` and `master` return a problem response "not available until SPEC-23" and create no job.
- Limits (NFR-12): container CPU and memory caps in `compose.yaml`; per job `timeoutSec` and `maxMemoryMb` enforced on the child process; VideoSpec byte size and object and action counts checked against `capabilities.json` limits before work.
- Remotion toolchain present in the image (`@remotion/renderer`, Chrome Headless Shell ensured at build) and proven by a test-only one-frame probe composition registered only when `APP_ENV=test`.
- Remotion licence note in `media/scenes/README.md` (free individual licence, ADR-002).

Out: the compiler (SPEC-16); scene families (SPEC-19, SPEC-20); clips, cache and assembly (SPEC-23); media QA (SPEC-24).

## Design
Rules: [media.mdc](../../../../.cursor/rules/media.mdc) (Typed specs only; Rendering, cache and manifest). The render service never writes outside the `media` schema and never deletes objects. Expected diff: about 380 lines.

## Acceptance criteria
- AC1 (NFR-12): Given the same `RenderJobRequest` twice, when posted, then one job exists and both responses carry the same `jobId` and status.
- AC2 (R-18 via schema): Given a `validate` job for the odd-squares VideoSpec, then it succeeds; given a schema-level invalid fixture, then it fails with the fixture's expected code naming the scene and field.
- AC3 (NFR-12): Given a VideoSpec over the byte, object or action limits, when posted, then it is rejected before any work with `resource_limit` and `oos.render.limit_breach{limit}` increments.
- AC4 (NFR-12): Given a test job that exceeds `timeoutSec` or `maxMemoryMb`, then the child is stopped, the job ends `failed` with `resource_limit`, and the service stays healthy.
- AC5: Given a render process killed mid-job, when its lease expires, then another claim picks it up and `attempts` increments.
- AC6: Given the image, when the test-only probe composition renders one frame, then a PNG is produced (Remotion and Chrome work in the container).

## Tests
- T-40 functional: idempotency by input hash, size and count limits, time and memory caps, lease recovery (AC1–AC5). Media unit in `media/scenes/tests/`: Ajv validation of the fixtures, probe render (AC2, AC6).

## Observability
Spans `render.job` → `compile` (validation at M0); metrics `oos.render.duration_seconds{kind}`, peak memory and CPU per job, `oos.render.limit_breach{limit}`; log event `render.resource_limit` (pino, OBSERVABILITY.md). Add a render panel to the Stack health dashboard.

## Dependencies
SPEC-03d (generated media types), SPEC-05 (object store and credentials). Contracts: 1.0.0 media. Size M (2 spec-days).
