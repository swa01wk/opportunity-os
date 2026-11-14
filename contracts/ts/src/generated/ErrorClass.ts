/* eslint-disable */

/**
 * R-53 classification. Each class has its own repair options.
 */
export type ErrorClass =
  | "retryable_provider"
  | "invalid_content"
  | "render_defect"
  | "uncertain_external"
  | "resource_limit"
  | "authorization"
  | "conflict"
  | "internal";
