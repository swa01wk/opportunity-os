# ADR-013: Text-to-speech provider for the narrator
Status: Proposed — awaiting your decision (Q-06); narrator licence needs a specialist    Date: 2026-11-12

## Context
One licensed English narrator (NFR-16). Measured timing, not estimates, drives scenes and captions, so the provider must return word- or character-level timestamps (R-26). The operator must fix pronunciation, including notation such as "n squared" (R-25). The licence must allow commercial use of the synthetic voice on YouTube and Instagram (A-06, specialist review). Cost is recorded per take (R-35).

## Options

| | A. ElevenLabs | B. Azure AI Speech | C. Google Cloud Text-to-Speech | D. Any TTS + our forced aligner |
|---|---|---|---|---|
| Timing data | Character-level `alignment` returned with the audio ("convert with timestamps") [ElevenLabs](https://elevenlabs.io/docs/api-reference/streaming-with-timestamps) | Word-boundary events from the Speech SDK | Only at SSML `<mark>` points you insert | Whatever the aligner produces |
| Pronunciation | Pronunciation dictionaries (up to 3 per request) | SSML phonemes and custom lexicons | SSML phonemes | Provider-dependent |
| Voice quality | Strong narration voices | Strong neural voices | Good | Provider-dependent |
| Region | Vendor-hosted | Central India region available | asia-south1 available | — |
| Commercial voice rights | Depends on plan tier; check for YouTube/Instagram | Standard neural voices licensed for product use; custom voices gated | Standard voices licensed for product use | Provider-dependent |
| Extra work | Least | SDK event plumbing | Insert marks per phrase | We own an alignment model (more to evaluate) |

## Recommendation
**A. ElevenLabs** as the narrator provider for quality and built-in alignment, with **B. Azure** as the fallback adapter. Decide after an M0 audition of the odd-squares script on both (pronunciation, pacing, alignment accuracy, cost per minute).

## Decision
Pending. No TTS call is made until you approve the provider and the narrator licence is confirmed by a specialist.
