/* eslint-disable */

/**
 * Durable request written by the API in the same transaction as the command (ADR-003). The dispatcher starts a DBOS workflow whose ID equals requestId, so lost acknowledgements and duplicate dispatch start at most one workflow.
 */
export interface WorkflowRequest {
  input: {
    contractRef?: VersionRef;
    estimatedCost?: Money;
    packageRef?: VersionRef;
    revisionId?: string;
    /**
     * @maxItems 24
     *
     * Items: Stable, human-readable ID unique within its document (objects, elements, scenes, beats, phrases).
     */
    sceneIds?: string[];
    scriptRef?: VersionRef;
    storyboardRef?: VersionRef;
  };
  /**
   * Absolute UTC timestamp (RFC 3339). Display timezone is a destination setting (R-04).
   */
  notBefore?: string;
  projectId: string;
  requestId: string;
  requestedBy: Actor;
  workflowType:
    | "research"
    | "script"
    | "storyboard"
    | "narration"
    | "preview"
    | "master"
    | "revision"
    | "revision_redraft"
    | "package_build"
    | "export_build"
    | "data_export"
    | "retention_sweep"
    | "project_deletion"
    | "diagnostic";
}
/**
 * Pointer to one immutable version of a record. Approvals and manifests bind to these.
 */
export interface VersionRef {
  id: string;
  /**
   * Lowercase hex SHA-256 of canonical JSON (RFC 8785) or of file bytes.
   */
  sha256: string;
  version: number;
}
/**
 * Run estimate checked against the remaining allowance at request time (R-07). Each task still reserves its own cost before dispatch (R-34).
 */
export interface Money {
  /**
   * Amount in minor units (paise, cents).
   */
  amountMinor: number;
  currency: string;
  /**
   * Recorded conversion rate into the reporting currency (INR, Q-05), as a decimal string.
   */
  fxRateToReporting?: string;
}
export interface Actor {
  id: string;
  /**
   * PRD §2.3 responsibility the action was taken under (R-05). Only members have one.
   */
  responsibility?: "owner" | "editor" | "reviewer" | "publisher" | "analyst";
  type: "member" | "service" | "agent_task";
}
