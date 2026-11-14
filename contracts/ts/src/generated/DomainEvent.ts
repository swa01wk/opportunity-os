/* eslint-disable */

/**
 * Outbox event (ADR-010). Written in the same transaction as the change it reports. Events are facts for projection, Studio updates and audit; they never carry authority. Consumers are idempotent by eventId and re-read current state before acting.
 */
export type DomainEvent = {
  actor: Actor;
  /**
   * Event or command that caused this one.
   */
  causationId?: string;
  /**
   * Run or request that this event belongs to.
   */
  correlationId: string;
  eventId: string;
  /**
   * Payload version for this type.
   */
  eventVersion: number;
  /**
   * Absolute UTC timestamp (RFC 3339). Display timezone is a destination setting (R-04).
   */
  occurredAt: string;
  payload: {};
  projectId?: string;
  subject: {
    id: string;
    type: string;
    version?: number;
  };
  traceparent?: string;
  type: EventType;
  workspaceId: string;
};
export type EventType =
  | "project.state_changed"
  | "contract.version_created"
  | "claim.created"
  | "claim.status_changed"
  | "demonstration.version_created"
  | "script.version_created"
  | "storyboard.version_created"
  | "narration.take_created"
  | "approval.recorded"
  | "approval.invalidated"
  | "workflow.requested"
  | "run.state_changed"
  | "run.cancelled"
  | "task_attempt.started"
  | "task_attempt.finished"
  | "budget.reserved"
  | "budget.settled"
  | "budget.released"
  | "budget.exhausted"
  | "render.completed"
  | "revision.redraft_ready"
  | "revision.applied"
  | "finding.raised"
  | "finding.resolved"
  | "rubric.scored"
  | "package.version_created"
  | "package.exported"
  | "publication.recorded"
  | "publication.verified"
  | "correction.proposed"
  | "metric.snapshot_recorded"
  | "asset.registered"
  | "effort.recorded"
  | "project.archived"
  | "project.deletion_requested"
  | "project.deleted"
  | "kpi.baseline_recorded";

export interface Actor {
  id: string;
  /**
   * PRD §2.3 responsibility the action was taken under (R-05). Only members have one.
   */
  responsibility?: "owner" | "editor" | "reviewer" | "publisher" | "analyst";
  type: "member" | "service" | "agent_task";
}
