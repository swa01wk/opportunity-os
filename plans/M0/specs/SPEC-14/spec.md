# SPEC-14: Search API choice and SearchProvider adapter (Q-29)
Milestone: M0 | Status: Draft (ready when SPEC-11a merges) | Layer: agent
Agent (if any): tool `search_sources` for the research task (task maturity target L3, Q-33); eval scenarios: none here (research suite in SPEC-33); conformance: C02 path only (C06 is SPEC-33's)
Requirements: R-08, NFR-11 | Feature: F-03 | ADRs: ADR-009, ADR-014; new ADR-023 (search provider)
Screens: — | Branch: `feat/SPEC-14-search-provider`

## Goal
The research task has a `search_sources` tool backed by a chosen web search API behind a `SearchProvider` adapter, so Q-29 is closed before M2 needs it.

## Scope
In:
- Desk comparison of at least three web search APIs with official, documented APIs, on: result quality for six synthetic queries drawn from the Strategy §5.1 topics; terms (storing titles, URLs and snippets; use with an LLM; attribution); price per 1,000 queries and free tier; rate limits; data retention; availability from India. Providers that obtain results by scraping another search engine are excluded (NFR-18). Results table in ADR-023.
- ADR-023 "Search provider" (tech lead decision per Q-29; Accepted in this PR unless you object in review), Q-29 closed in QUESTIONS.md, TECH_STACK.md row filled.
- `SearchProvider` port in `backend/opportunityos/adapters/search/` (ADR-009): `search(query, limit) -> list[SearchResult]` mapped to the `search_sources` output in `tools.schema.json`; the chosen implementation (httpx), a deterministic fake serving fixture results, and `estimate_cost`.
- `search_sources` registered in the tool host (SPEC-11a) as read-only.
- `SEARCH_API_KEY` in `.env` only; until you create the account, the operator-URL path (A-29) keeps working.

Out: fetching and extracting pages (SPEC-32); the research task (SPEC-33).

## Design
Search results are untrusted data (agent.mdc); only titles, URLs, snippets and ranks enter the task, delimited as data. Expected diff: about 300 lines plus the ADR.

## Acceptance criteria
- AC1 (NFR-11): Given the shared adapter fixtures, when run against the fake and (with `LIVE=1`) the chosen provider, then both return results that validate against the `search_sources` output schema.
- AC2: Given a provider error, timeout or rate limit, then the adapter raises `retryable_provider` with no partial results stored.
- AC3 (R-08): Given a model call to `search_sources` from a task that does not permit it, then the tool host denies it (C02 path from SPEC-11a).
- AC4: Given ADR-023, then it records every candidate with the comparison criteria, the choice, its cost and terms, and the exclusion rule for scraping-based providers.

## Tests
- T-42 functional: adapter conformance for the fake (every PR) and the chosen provider (weekly live) (AC1, AC2). Agent mocked: denied when not permitted (AC3).

## Observability
Span `tool.search_sources` with result count and provider latency; metrics `oos.agent.tool_calls{tool=search_sources}` and provider errors; no query text in telemetry beyond its hash.

## Dependencies
SPEC-11a (tool host). Contracts: 1.0.0 `tools.schema.json`. Size M (2 spec-days). Your dependency after merge: create the search account and put the key in `.env` (DELIVERY_PLAN.md dependencies).
