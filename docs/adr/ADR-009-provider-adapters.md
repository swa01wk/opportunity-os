# ADR-009: Every external provider sits behind an adapter
Status: Accepted (individual providers: ADR-011–ADR-014)    Date: 2026-11-12

## Context
LLM, TTS, auth, storage and publishing providers will change (NFR-11, A-06). Costs must be estimated and recorded per call (R-34, R-35), calls must be versioned for provenance (R-50, R-54), and no provider is called before you approve it (A-06).

## Decision
Python protocols in `backend/adapters/` (and `agent/llm/`, `media/audio/tts/`), each with a fake used in tests and the eval mock mode:

| Port | Methods (sketch) | Records per call |
|---|---|---|
| `LlmProvider` | `complete(request: TaskPrompt, output_schema, tools) -> ModelResult` | provider, model ID, prompt hash, tokens, cost, latency |
| `TtsProvider` | `synthesize(text, voice, pronunciations) -> AudioWithAlignment` | provider, voice ID, settings, characters, cost; alignment must be word- or character-timed (R-26) |
| `IdentityProvider` | `verify(token) -> Principal` | issuer, subject, MFA claim |
| `BlobStore` | `put(bytes, sha256)`, `signed_get(key, ttl)` | key, size, hash |
| `SourceFetcher` | `fetch(url, limits) -> UntrustedDocument` | final URL, status, bytes, content type |
| `PublishingAdapter` (R3) | `upload_private`, `get_status`, `release`, `schedule`, `cancel` | external IDs, request IDs |

Rules: adapters return typed contracts, never provider objects; each declares `estimate_cost(request)` used for budget reservation; secrets come from the environment (vault outside local); model and voice IDs are configuration, pinned per run. `SourceFetcher` refuses private-network and metadata addresses, follows a bounded number of redirects, caps size and validates content type (NFR-05).

## Alternatives
- **Call SDKs directly from tasks:** fast to start, breaks portability, cost capture and test mocking.
- **A third-party LLM gateway:** another service in the critical path; can still be added behind `LlmProvider` later.

## Consequences
- Easier: provider swaps, deterministic tests and the mocked eval suite (`make eval`).
- Harder: lowest-common-denominator interfaces; provider-specific features (prompt caching, pronunciation dictionaries) go through optional capability flags.
