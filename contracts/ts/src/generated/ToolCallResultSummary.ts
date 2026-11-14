/* eslint-disable */

export interface ToolCallResultSummary {
  count?: number;
  outcome: "ok" | "refused" | "denied" | "failed";
  /**
   * Coded, never free text from a page or the model.
   */
  reason?:
    | "not_permitted"
    | "budget"
    | "ssrf_guard"
    | "not_in_search_results"
    | "timeout"
    | "provider_error"
    | "injection_suspected"
    | "other";
}
