# SPEC-05: Object store choice and BlobStore adapter (ADR-015 amendment)
Milestone: M0 | Status: Draft (ready when SPEC-01a merges) | Layer: backend
Agent (if any): —
Requirements: R-30, NFR-04 | Feature: F-08 | ADRs: ADR-015, ADR-007, ADR-009
Screens: — | Branch: `feat/SPEC-05-object-store`

## Goal
The stack runs an actively maintained S3-compatible store chosen by a conformance suite, and every service reaches it through a `BlobStore` port with content-addressed keys, short-lived signed reads and per-service credentials that cannot delete.

## Scope
In:
- `BlobStore` port in `backend/opportunityos/adapters/blob/` with an S3 implementation (boto3) and an in-memory fake: `put(bytes|stream) -> BlobRef` (key `sha256/<hash>`, `If-None-Match: *`), `get`, `head`, `sign_get(ref, ttl=900)`.
- Conformance suite run against the interim MinIO image and both candidates in ADR-015 (SeaweedFS, Garage): put and get, hash check, conditional put, presigned GET that expires, per-credential policy (`worker` and `render` put and get, no delete; `api_signer` sign and read only; `retention` delete), versioning or object lock if offered.
- Decision: the store that passes the suite with the fewest exceptions, ties broken by maintenance activity and image provenance. It replaces the interim image in `compose.yaml` (pinned by digest), with a bootstrap script in `infra/objectstore/` that creates the bucket and the four credentials from `.env`.
- Docs: amendment line in ADR-015 with the result table; TECH_STACK.md storage row; SECURITY.md accepted risk for the interim MinIO image closed; STATUS.md risk line updated.

Out: the Node client in `render` (SPEC-12); retention (SPEC-69); AWS S3 (after the R2 gate).

## Design
- Immutability does not depend on a store feature (ADR-015): content-addressed keys, insert-only rows, no delete credential.
- Signed URLs are 15 minutes and never logged with their query string (OBSERVABILITY.md redaction).
- Expected diff: about 350 lines.

## Acceptance criteria
- AC1 (R-30): Given an object put by `worker`, when `worker` or `render` tries to delete or overwrite it, then the store refuses; when the same bytes are put again, then the same key is returned and nothing changes.
- AC2 (NFR-04): Given a signed GET from `sign_get`, when used within 15 minutes, then it returns the object; after expiry, then it is refused.
- AC3: Given the `api_signer` credential, when it tries to put, then it is refused.
- AC4: Given bytes whose hash differs from the requested key, when `put` verifies, then it raises and logs `blob.hash_mismatch`.
- AC5: Given the conformance results, then ADR-015 has an amendment naming the chosen store, its version and digest, and every check's result per candidate.

## Tests
- T-35 functional: the BlobStore conformance suite against the chosen store (Testcontainers) and the fake; the candidate comparison is run once and its output attached to the PR (AC1–AC5).

## Observability
Spans `blob.put`, `blob.sign`; metrics bytes stored, put errors, signed URLs issued; log event `blob.hash_mismatch` (OBSERVABILITY.md).

## Dependencies
SPEC-01a. Contracts: `BlobRef` in common.schema.json (0.4.0 set). Size M (2 spec-days).
