# ADR-015: Local object store after MinIO Community Edition was retired
Status: Accepted    Date: 2026-11-13

## Context
ADR-007 and ADR-011 named MinIO in Docker Compose as the local S3-compatible store. During Stage 2b we found that MinIO's community edition is no longer actively developed and is distributed as source only, without official images ([linuxiac](https://linuxiac.com/minio-ends-active-development/), [itsfoss](https://itsfoss.com/news/minio-moves-away-from-open-source/)). Unpatched storage software in the stack is a supply-chain risk (SECURITY.md). Requirements: R-30, NFR-04, NFR-10, NFR-13. The design already depends only on the S3 API (ADR-007, ADR-011), so the store is replaceable.

## Decision
- Immutability of approved artifacts does **not** rely on a storage-product feature locally. It is guaranteed by content-addressed keys, insert-only version rows, and per-service storage credentials with no delete grant for `worker` and `render`. Deletion is done only by the retention job's own credential (ADR-007).
- **Interim (now):** keep the last published MinIO community image, pinned by digest, bound to the Compose network only (no host port except the signed-URL endpoint on localhost). Documented as an accepted risk in SECURITY.md.
- **M0 storage spec** replaces it with an actively maintained S3-compatible store chosen by a conformance check: put/get, presigned GET with expiry, conditional put (`If-None-Match`), per-credential policies (no delete), versioning or object lock if offered. Candidates: SeaweedFS, Garage. The winner gets an amendment line in this ADR.
- **AWS (after the R2 gate, ADR-011):** S3 with Object Lock, unchanged.

## Alternatives
- **Keep MinIO unpinned / build from source ourselves:** we would own patching of a storage server.
- **Local filesystem behind the `BlobStore` port:** no signed URLs or per-credential policy, so local behaviour would differ from hosted.
- **Use real S3 now:** contradicts local-only (ADR-011).

## Consequences
- Easier: no feature of the local store is load-bearing for correctness.
- Harder: one more M0 task; `BlobStore` conformance tests must run against both the local store and S3 later.
- ADR-007's "Object Lock or versioning on" applies to S3; locally it is "if offered by the chosen store".
