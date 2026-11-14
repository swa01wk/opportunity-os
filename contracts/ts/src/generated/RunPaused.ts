/* eslint-disable */

export type Gate =
  "A_brief" | "B_explanation_script" | "C_storyboard" | "D_final_package" | "E_public_release";

export interface RunPaused {
  gate?: Gate;
  reason: "budget" | "awaiting_approval" | "manual_takeover" | "cancelling";
  /**
   * The one Studio action that unblocks the run (R-53, R-61).
   */
  unblockAction?: "raise_allowance" | "open_gate" | "take_over" | "none";
}
