/* eslint-disable */

export type Uuid = string;
/**
 * Absolute UTC timestamp (RFC 3339). Display timezone is a destination setting (R-04).
 */
export type Timestamp = string;

export interface AnalyticsEvent {
  eventName:
    | "video.approved"
    | "video.published"
    | "gate.approved"
    | "run.finished"
    | "effort.logged"
    | "kpi.baseline_recorded"
    | "cost.settled"
    | "rubric.scored"
    | "finding.resolved"
    | "metric.recorded";
  eventVersion: number;
  memberId?: Uuid;
  occurredAt: Timestamp;
  projectId?: Uuid;
  properties: {};
  sourceEventId: Uuid;
  workspaceId: Uuid;
}
