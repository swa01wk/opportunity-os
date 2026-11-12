# ADR-014: OpenAI GPT-5.4 mini for the three agent tasks
Status: Accepted    Date: 2026-11-12 (decided by the product owner; Q-06)

## Context
There are three bounded tasks (R-63): research, script and storyboard. Each needs:
- output constrained to a schema;
- read-only tool calls (`docs/contracts/agent-tools/`);
- resistance to prompt injection from fetched pages (NFR-05);
- pinned model versions and a recorded cost for every call (R-50, R-35);
- evaluation across all four series (NFR-17).

The provider must stay swappable (ADR-009).

## Decision
- **Model:** `gpt-5.4-mini`, pinned to the dated snapshot **`gpt-5.4-mini-2026-03-17`** ([OpenAI model page](https://developers.openai.com/api/docs/models/gpt-5.4-mini)).
  - Context window: 400k tokens.
  - Output: up to 128k tokens.
  - Supports structured outputs and function calling.
- **Structured outputs** carry each task's output schema (`task-io.schema.json`), and **function calling** carries the tools (`tools.schema.json`). A response that fails our own Pydantic validation counts as `schema_invalid` and uses up one of the task's retries.
- **Reasoning effort per task** is set in config and recorded with each attempt. Starting values: `medium` for research and storyboard, `low` for script. They are tuned on the R0 evaluation fixtures.
- **The provider's built-in web search is not used.** Research goes through our `search_sources` / `fetch_source` tools, so every source is recorded, size-bounded and SSRF-checked (R-08, NFR-05).
- **Cost:** the adapter estimates cost before each call for reservation and records actual tokens and cost afterwards. List price on 2026-11-12 is USD 0.75 per 1M input tokens, 0.075 per 1M cached input and 4.50 per 1M output. Prices sit in configuration, not code, and are converted to INR at a recorded rate (Q-05).
- **Knowledge cutoff** (August 2025) does not limit research, which works from fetched sources. Script and storyboard tasks work only from approved claims.

## Alternatives
- **Evaluating two providers before choosing:** dropped by the owner's decision; the adapter and evaluation suite still allow a later switch.
- **A larger model tier:** higher cost per task; reconsider per task only if the R0 evaluation shows a quality gap.

## Consequences
- Development runs on free credits; cost is recorded per call (Q-05).
- Before the first real call:
  - An OpenAI API key, in `.env` locally and Secrets Manager on AWS.
  - Data-use terms recorded in SECURITY.md (Stage 2b).
- Changing the snapshot or reasoning effort is a versioned config change that must pass the evaluation suite (NFR-17).
- Synthetic data only in prompts and fixtures (A-23).
