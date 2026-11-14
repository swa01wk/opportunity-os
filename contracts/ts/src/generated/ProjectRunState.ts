/* eslint-disable */

/**
 * Workflow step names shown in the run indicator and S-13.
 */
export type StepName = string;
export type Gate =
  "A_brief" | "B_explanation_script" | "C_storyboard" | "D_final_package" | "E_public_release";
export type Uuid = string;
export type ProductionState =
  | "DRAFT"
  | "RESEARCHING"
  | "SCRIPT_REVIEW"
  | "STORYBOARD_REVIEW"
  | "PRODUCING"
  | "QA"
  | "FINAL_REVIEW"
  | "APPROVED_EXPORT"
  | "BLOCKED"
  | "FAILED"
  | "REVISION_REQUIRED"
  | "CANCELLED";

export interface ProjectRunState {
  activeRuns: {
    currentStep?: StepName;
    paused?: RunPaused;
    runId: Uuid;
    status: "pending" | "running" | "paused" | "cancelling";
    stepCount?: number;
    stepIndex?: number;
    workflowType: string;
  }[];
  /**
   * outbox seq this snapshot reflects; the stream continues after it.
   */
  asOfSeq: number;
  /**
   * Why the project is blocked or waiting, so the Studio can say what unblocks it.
   */
  blockers?: {
    code: string;
    unblockAction: string;
  }[];
  productionState?: ProductionState;
  projectId: Uuid;
}
export interface RunPaused {
  gate?: Gate;
  reason: "budget" | "awaiting_approval" | "manual_takeover" | "cancelling";
  /**
   * The one Studio action that unblocks the run (R-53, R-61).
   */
  unblockAction?: "raise_allowance" | "open_gate" | "take_over" | "none";
}
