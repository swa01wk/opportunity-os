/* eslint-disable */

/**
 * Never page text, prompts, model output, secrets or signed URLs (SECURITY TH-31).
 */
export interface ToolCallArgsSummary {
  /**
   * Host of a fetched URL only, e.g. example.org
   */
  domain?: string;
  queryCount?: number;
  tool:
    | "search_sources"
    | "fetch_source"
    | "compute_demonstration"
    | "list_capabilities"
    | "validate_scene_spec";
}
