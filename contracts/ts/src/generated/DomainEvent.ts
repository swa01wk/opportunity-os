/* eslint-disable */

export type Uuid = string;
/**
 * Absolute UTC timestamp (RFC 3339). Display timezone is a destination setting (R-04).
 */
export type Timestamp = string;
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

export interface DomainEvent {
  actor: Actor;
  causationId?: Uuid;
  correlationId: Uuid;
  eventId: Uuid;
  /**
   * Payload version for this type.
   */
  eventVersion: number;
  occurredAt: Timestamp;
  payload: {};
  projectId?: Uuid;
  subject: {
    id: Uuid;
    type: string;
    version?: number;
  };
  traceparent?: string;
  type: EventType;
  workspaceId: Uuid;
}
export interface Actor {
  id: string;
  /**
   * PRD §2.3 responsibility the action was taken under (R-05). Only members have one.
   */
  responsibility?: "owner" | "editor" | "reviewer" | "publisher" | "analyst";
  type: "member" | "service" | "agent_task";
}
