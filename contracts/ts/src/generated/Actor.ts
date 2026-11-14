/* eslint-disable */

export interface Actor {
  id: string;
  /**
   * PRD §2.3 responsibility the action was taken under (R-05). Only members have one.
   */
  responsibility?: "owner" | "editor" | "reviewer" | "publisher" | "analyst";
  type: "member" | "service" | "agent_task";
}
