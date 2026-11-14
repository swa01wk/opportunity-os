/* eslint-disable */

/**
 * KPI analytics event (ADR-017). Written only by the outbox relay into analytics.event from a delivered DomainEvent; never written directly. Properties carry no free text and no personal data beyond the member UUID. Event names and KPIs: OBSERVABILITY.md. R3 adds recommendation.decided.
 */
export type AnalyticsEvent = {
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
  memberId?: string;
  /**
   * Absolute UTC timestamp (RFC 3339). Display timezone is a destination setting (R-04).
   */
  occurredAt: string;
  projectId?: string;
  properties: {};
  sourceEventId: string;
  workspaceId: string;
};
