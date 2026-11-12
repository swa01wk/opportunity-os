# ADR-014: LLM provider for research, script and storyboard tasks
Status: Proposed — awaiting your decision (Q-06)    Date: 2026-11-12

## Context
Three bounded tasks (R-63): research (sources → claims with locations), script (beats with claim IDs), storyboard (VideoSpec within the capability catalogue). Each needs schema-constrained output, tool use for read-only tools (`docs/contracts/agent-tools/`), resistance to prompt injection in fetched pages (NFR-05), pinned model versions and per-call cost (R-50, R-35). Evaluation decides quality (NFR-17). Provider must be swappable (ADR-009). Disclosure: this ADR was drafted by Claude, an Anthropic model, which is one of the options.

## Options

| | A. Anthropic (Claude API) | B. OpenAI | C. Google (Gemini API) |
|---|---|---|---|
| Structured output | JSON-schema tool output | JSON-schema structured outputs | JSON-schema response format |
| Tool use | Yes | Yes | Yes |
| Long source context | Large context windows | Large context windows | Very large context windows |
| Built-in web search | Available as a server tool | Available as a tool | Grounding with Search |
| Version pinning | Dated model IDs | Dated model IDs | Versioned model IDs |
| Data use | API data not used for training by default (check terms) | Same (check terms) | Paid tier terms (check) |

Built-in web search tools are **not** used: research goes through our `search_sources` / `fetch_source` tools so that every source is recorded, size-bounded and SSRF-checked (NFR-05, R-08).

## Recommendation
Wire **two** providers behind `LlmProvider` in M0 (A and B are both credible on schema-constrained tool use), run the R0 evaluation fixtures (odd-squares plus one brief from another series) on both, and choose the primary by task success, claim accuracy, schema-valid rate and cost per task. Use one model tier per task, pinned in config.

## Decision
Pending your choice of the two candidates to evaluate (or a single provider if you prefer to skip the comparison). No paid call before approval and before Q-05 budget limits are set.
