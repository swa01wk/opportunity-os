# ADR-013: ElevenLabs for narration
Status: Accepted    Date: 2026-11-12 (decided by the product owner; Q-06)

## Context
- There is one licensed English narrator (NFR-16).
- Measured timing, not estimates, drives scenes and captions, so the provider must return timestamps (R-26).
- The operator must be able to fix pronunciation, including notation (R-25).
- Each take's cost is recorded (R-35).
- The voice licence must allow commercial use on YouTube and Instagram (A-06).

Options proposed in Stage 2a: ElevenLabs, Azure AI Speech, Google Cloud TTS, or any TTS plus our own forced aligner.

## Decision
- **ElevenLabs** behind the `TtsProvider` adapter (ADR-009), using the "convert with timestamps" endpoint.
  - The endpoint returns audio with a character-level `alignment` ([ElevenLabs](https://elevenlabs.io/docs/api-reference/streaming-with-timestamps)).
  - `media.audio` turns that alignment into the word and phrase times in `timing.schema.json`, with `alignmentSource = provider_characters`.
- **Pronunciation:** the workspace pronunciation list (`/pronunciations`) is synced to an ElevenLabs pronunciation dictionary. Its ID and version are pinned in each take (`pronunciationSetSha256`). ElevenLabs allows up to 3 dictionaries per request.
- **Pinning:** `voiceId`, `modelId` and voice settings are set in configuration and pinned per take (R-03). Changing any of them invalidates every affected scene (R-32).
- **Narrator licence rule** (tech-lead decision 2026-11-13, Q-06). The free plan carries no commercial licence ([ElevenLabs](https://elevenlabs.io/docs/help-center/legal/can-i-publish-the-content-i-generate-on-the-platform)), and content made on a paid plan stays commercially usable after cancelling.
  - Development on free credits is fine.
  - Any take in a published package must be generated on a paid plan, using a default or library voice licensed for commercial use, or the owner's own voice. Never a clone of another person.
  - Each take records `licence.plan` and `licence.commercialUse` (`timing.schema.json`). The voice is registered in the rights ledger. Gate D is blocked while any take in the package has `commercialUse = false` (R-55 AC2).
- **No fallback provider is wired now.** The adapter and its shared fixtures keep a second provider possible later (NFR-11).

## Alternatives
- **Azure AI Speech:** good voices and word-boundary events, but more plumbing; kept as the documented fallback.
- **Google Cloud TTS:** timing only at inserted SSML marks.
- **Our own forced aligner:** another model to run and evaluate.

## Consequences
- Development runs on free credits; cost is still recorded per take (Q-05).
- Before the first public upload (R2): switch to a paid plan and regenerate any free-plan takes in the package. The Gate D blocker enforces this.

Separately, the API key lives in `.env` locally (git-ignored) and in Secrets Manager on AWS (NFR-06).
