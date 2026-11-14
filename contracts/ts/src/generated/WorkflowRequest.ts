/* eslint-disable */

export type Uuid = string;
/**
 * Lowercase hex SHA-256 of canonical JSON (RFC 8785) or of file bytes.
 */
export type Sha256 = string;
/**
 * Stable, human-readable ID unique within its document (objects, elements, scenes, beats, phrases).
 */
export type LocalId = string;
/**
 * Absolute UTC timestamp (RFC 3339). Display timezone is a destination setting (R-04).
 */
export type Timestamp = string;

export interface WorkflowRequest {
  input: {
    contractRef?: VersionRef;
    estimatedCost?: Money;
    packageRef?: VersionRef;
    revisionId?: Uuid;
    /**
     * @maxItems 24
     */
    sceneIds?: LocalId[];
    scriptRef?: VersionRef;
    storyboardRef?: VersionRef;
  };
  notBefore?: Timestamp;
  projectId: Uuid;
  requestId: Uuid;
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
  id: Uuid;
  sha256: Sha256;
  version: number;
}
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
