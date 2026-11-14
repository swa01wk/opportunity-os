"""DomainEvent and payload types (events/domain-event.schema.json)."""

from enum import StrEnum
from typing import Annotated, Any, Final, Self

from pydantic import ConfigDict, Field, StringConstraints, model_validator

from opportunityos_contracts._schema import ContractModel
from opportunityos_contracts.common import (
    Actor,
    ErrorClass,
    Money,
    Sha256,
    Timestamp,
    Uuid,
    VersionRef,
)
from opportunityos_contracts.events.workflow_request import WorkflowRequest
from opportunityos_contracts.validators import JsonInt, reject_explicit_null_keys

DOMAIN_OPTIONAL_FIELDS: Final = frozenset({"projectId", "causationId", "traceparent"})
SUBJECT_OPTIONAL_FIELDS: Final = frozenset({"version"})


class EventType(StrEnum):
    PROJECT_STATE_CHANGED = "project.state_changed"
    CONTRACT_VERSION_CREATED = "contract.version_created"
    CLAIM_CREATED = "claim.created"
    CLAIM_STATUS_CHANGED = "claim.status_changed"
    DEMONSTRATION_VERSION_CREATED = "demonstration.version_created"
    SCRIPT_VERSION_CREATED = "script.version_created"
    STORYBOARD_VERSION_CREATED = "storyboard.version_created"
    NARRATION_TAKE_CREATED = "narration.take_created"
    APPROVAL_RECORDED = "approval.recorded"
    APPROVAL_INVALIDATED = "approval.invalidated"
    WORKFLOW_REQUESTED = "workflow.requested"
    RUN_STATE_CHANGED = "run.state_changed"
    RUN_CANCELLED = "run.cancelled"
    TASK_ATTEMPT_STARTED = "task_attempt.started"
    TASK_ATTEMPT_FINISHED = "task_attempt.finished"
    BUDGET_RESERVED = "budget.reserved"
    BUDGET_SETTLED = "budget.settled"
    BUDGET_RELEASED = "budget.released"
    BUDGET_EXHAUSTED = "budget.exhausted"
    RENDER_COMPLETED = "render.completed"
    REVISION_REDRAFT_READY = "revision.redraft_ready"
    REVISION_APPLIED = "revision.applied"
    FINDING_RAISED = "finding.raised"
    FINDING_RESOLVED = "finding.resolved"
    RUBRIC_SCORED = "rubric.scored"
    PACKAGE_VERSION_CREATED = "package.version_created"
    PACKAGE_EXPORTED = "package.exported"
    PUBLICATION_RECORDED = "publication.recorded"
    PUBLICATION_VERIFIED = "publication.verified"
    CORRECTION_PROPOSED = "correction.proposed"
    METRIC_SNAPSHOT_RECORDED = "metric.snapshot_recorded"
    ASSET_REGISTERED = "asset.registered"
    EFFORT_RECORDED = "effort.recorded"
    PROJECT_ARCHIVED = "project.archived"
    PROJECT_DELETION_REQUESTED = "project.deletion_requested"
    PROJECT_DELETED = "project.deleted"
    KPI_BASELINE_RECORDED = "kpi.baseline_recorded"


class ProductionState(StrEnum):
    DRAFT = "DRAFT"
    RESEARCHING = "RESEARCHING"
    SCRIPT_REVIEW = "SCRIPT_REVIEW"
    STORYBOARD_REVIEW = "STORYBOARD_REVIEW"
    PRODUCING = "PRODUCING"
    QA = "QA"
    FINAL_REVIEW = "FINAL_REVIEW"
    APPROVED_EXPORT = "APPROVED_EXPORT"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    REVISION_REQUIRED = "REVISION_REQUIRED"
    CANCELLED = "CANCELLED"


class ProjectStateChanged(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    from_state: Annotated[ProductionState, Field(alias="from")]
    to: ProductionState
    reason: Annotated[str | None, Field(default=None, max_length=500)] = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_null_reason(cls, data: Any) -> Any:
        return reject_explicit_null_keys(data, frozenset({"reason"}))


class Gate(StrEnum):
    A_BRIEF = "A_brief"
    B_EXPLANATION_SCRIPT = "B_explanation_script"
    C_STORYBOARD = "C_storyboard"
    D_FINAL_PACKAGE = "D_final_package"
    E_PUBLIC_RELEASE = "E_public_release"


class ApprovalTargetType(StrEnum):
    CONTRACT = "contract"
    SCRIPT = "script"
    DEMONSTRATION = "demonstration"
    STORYBOARD = "storyboard"
    PACKAGE = "package"
    RELEASE_INSTRUCTION = "release_instruction"


class ApprovalTarget(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    type: ApprovalTargetType
    ref: VersionRef


class PolicyVersions(ContractModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        json_schema_extra={
            "description": (
                "Policy versions in force when an approval was recorded (R-41 AC3, Q-35)."
            ),
        },
    )

    brand_kit: Annotated[VersionRef, Field(alias="brandKit")]
    rubric: Annotated[str, Field(max_length=40)]
    content_policy: Annotated[str, Field(alias="contentPolicy", max_length=40)]


class ApprovalDecision(StrEnum):
    APPROVED = "approved"
    RETURNED = "returned"


class ApprovalRecorded(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    approval_id: Annotated[Uuid, Field(alias="approvalId")]
    gate: Gate
    decision: ApprovalDecision
    target: ApprovalTarget
    scope: Annotated[str, Field(max_length=200)]
    destination_id: Annotated[Uuid | None, Field(default=None, alias="destinationId")] = None
    policy_versions: Annotated[
        PolicyVersions | None,
        Field(default=None, alias="policyVersions"),
    ] = None
    lapses_at: Annotated[Timestamp | None, Field(default=None, alias="lapsesAt")] = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_nulls(cls, data: Any) -> Any:
        return reject_explicit_null_keys(
            data,
            frozenset({"destinationId", "policyVersions", "lapsesAt"}),
        )


class ApprovalInvalidatedReason(StrEnum):
    TARGET_CHANGED = "target_changed"
    NEW_CLAIM = "new_claim"
    MATERIAL_VISUAL_CHANGE = "material_visual_change"
    MASTER_CHANGED = "master_changed"
    METADATA_CHANGED = "metadata_changed"
    DESTINATION_CHANGED = "destination_changed"
    SCHEDULE_CHANGED = "schedule_changed"
    REVOKED_BY_MEMBER = "revoked_by_member"
    POLICY_CHANGED = "policy_changed"
    RELEASE_TIME_LAPSED = "release_time_lapsed"


class ApprovalInvalidated(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    approval_id: Annotated[Uuid, Field(alias="approvalId")]
    gate: Gate
    reason: ApprovalInvalidatedReason
    cause_subject: Annotated[
        str | None,
        Field(default=None, alias="causeSubject", max_length=100),
    ] = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_null_cause(cls, data: Any) -> Any:
        return reject_explicit_null_keys(data, frozenset({"causeSubject"}))


class TaskType(StrEnum):
    RESEARCH = "research"
    SCRIPT = "script"
    STORYBOARD = "storyboard"
    DEMONSTRATION = "demonstration"
    NARRATION = "narration"
    TIMING = "timing"
    CAPTIONS = "captions"
    RENDER_VALIDATE = "render_validate"
    RENDER_CLIP = "render_clip"
    RENDER_PREVIEW = "render_preview"
    RENDER_MASTER = "render_master"
    MEDIA_QA = "media_qa"
    PACKAGE_BUILD = "package_build"
    EXPORT_BUILD = "export_build"


class TaskAttemptStatus(StrEnum):
    STARTED = "started"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    TIMED_OUT = "timed_out"
    CANCELLED = "cancelled"
    TAKEN_OVER = "taken_over"


class TaskAttempt(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    run_id: Annotated[Uuid, Field(alias="runId")]
    task_id: Annotated[str, Field(alias="taskId", max_length=100)]
    attempt_id: Annotated[Uuid, Field(alias="attemptId")]
    task_type: Annotated[TaskType, Field(alias="taskType")]
    attempt: Annotated[JsonInt, Field(ge=1)]
    status: TaskAttemptStatus
    error_class: Annotated[ErrorClass | None, Field(default=None, alias="errorClass")] = None
    estimated_cost: Annotated[Money | None, Field(default=None, alias="estimatedCost")] = None
    actual_cost: Annotated[Money | None, Field(default=None, alias="actualCost")] = None
    duration_ms: Annotated[JsonInt | None, Field(default=None, alias="durationMs", ge=0)] = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_nulls(cls, data: Any) -> Any:
        return reject_explicit_null_keys(
            data,
            frozenset(
                {"errorClass", "estimatedCost", "actualCost", "durationMs"},
            ),
        )


class BudgetChange(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    budget_id: Annotated[Uuid, Field(alias="budgetId")]
    amount: Money
    remaining: Money
    reservation_id: Annotated[Uuid | None, Field(default=None, alias="reservationId")] = None
    attempt_id: Annotated[Uuid | None, Field(default=None, alias="attemptId")] = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_nulls(cls, data: Any) -> Any:
        return reject_explicit_null_keys(data, frozenset({"reservationId", "attemptId"}))


class RenderOutputKind(StrEnum):
    PREVIEW = "preview"
    MASTER = "master"


class RenderCompleted(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    render_id: Annotated[Uuid, Field(alias="renderId")]
    output_kind: Annotated[RenderOutputKind, Field(alias="outputKind")]
    manifest_sha256: Annotated[Sha256, Field(alias="manifestSha256")]
    scenes_rebuilt: Annotated[JsonInt, Field(alias="scenesRebuilt", ge=0)]
    scenes_reused: Annotated[JsonInt, Field(alias="scenesReused", ge=0)]
    checks_failed: Annotated[JsonInt | None, Field(default=None, alias="checksFailed", ge=0)] = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_null_checks(cls, data: Any) -> Any:
        return reject_explicit_null_keys(data, frozenset({"checksFailed"}))


class RevisionApplied(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    revision_id: Annotated[Uuid, Field(alias="revisionId")]
    rebuilt: list[Annotated[str, Field(max_length=100)]]
    reused: list[Annotated[str, Field(max_length=100)]]
    reopened_gates: Annotated[list[Gate], Field(alias="reopenedGates")]
    duration_delta_frames: Annotated[
        JsonInt | None,
        Field(default=None, alias="durationDeltaFrames"),
    ] = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_null_delta(cls, data: Any) -> Any:
        return reject_explicit_null_keys(data, frozenset({"durationDeltaFrames"}))


class PublicationRoute(StrEnum):
    MANUAL = "manual"
    CONNECTED = "connected"


class PublicationState(StrEnum):
    PACKAGE_APPROVED = "PACKAGE_APPROVED"
    AWAITING_MANUAL_UPLOAD = "AWAITING_MANUAL_UPLOAD"
    UPLOAD_REQUESTED = "UPLOAD_REQUESTED"
    UPLOADING = "UPLOADING"
    UPLOADED_PRIVATE = "UPLOADED_PRIVATE"
    READY_TO_RELEASE = "READY_TO_RELEASE"
    RELEASE_REQUESTED = "RELEASE_REQUESTED"
    SCHEDULED = "SCHEDULED"
    PUBLISHED = "PUBLISHED"
    PUBLICATION_UNKNOWN = "PUBLICATION_UNKNOWN"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class PublicationVerification(StrEnum):
    NOT_CHECKED = "NOT_CHECKED"
    PASSED = "PASSED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


class PublicationRecorded(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    publication_id: Annotated[Uuid, Field(alias="publicationId")]
    package_ref: Annotated[VersionRef, Field(alias="packageRef")]
    route: PublicationRoute
    state: PublicationState
    verification: Annotated[PublicationVerification | None, Field(default=None)] = None
    package_mismatch: Annotated[bool | None, Field(default=None, alias="packageMismatch")] = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_nulls(cls, data: Any) -> Any:
        return reject_explicit_null_keys(
            data,
            frozenset({"verification", "packageMismatch"}),
        )


class DomainEventSubject(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    type: Annotated[str, StringConstraints(pattern=r"^[a-z_]{2,40}$")]
    id: Uuid
    version: Annotated[JsonInt | None, Field(default=None, ge=1)] = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_null_version(cls, data: Any) -> Any:
        return reject_explicit_null_keys(data, SUBJECT_OPTIONAL_FIELDS)


_TYPED_PAYLOAD: dict[EventType, type[ContractModel | WorkflowRequest]] = {
    EventType.PROJECT_STATE_CHANGED: ProjectStateChanged,
    EventType.APPROVAL_RECORDED: ApprovalRecorded,
    EventType.APPROVAL_INVALIDATED: ApprovalInvalidated,
    EventType.WORKFLOW_REQUESTED: WorkflowRequest,
    EventType.TASK_ATTEMPT_STARTED: TaskAttempt,
    EventType.TASK_ATTEMPT_FINISHED: TaskAttempt,
    EventType.BUDGET_RESERVED: BudgetChange,
    EventType.BUDGET_SETTLED: BudgetChange,
    EventType.BUDGET_RELEASED: BudgetChange,
    EventType.BUDGET_EXHAUSTED: BudgetChange,
    EventType.RENDER_COMPLETED: RenderCompleted,
    EventType.REVISION_APPLIED: RevisionApplied,
    EventType.PUBLICATION_RECORDED: PublicationRecorded,
}


class DomainEvent(ContractModel):
    """Outbox event (ADR-010).

    Written in the same transaction as the change it reports. Events are facts for projection,
    Studio updates and audit; they never carry authority. Consumers are idempotent by eventId
    and re-read current state before acting.
    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        json_schema_extra={
            "$comment": (
                "The if/then block above is for the JSON Schema draft only. The Pydantic source "
                "(ADR-008) models this as a discriminated union on `type`."
            ),
        },
    )

    event_id: Annotated[Uuid, Field(alias="eventId")]
    type: EventType
    event_version: Annotated[JsonInt, Field(alias="eventVersion", ge=1)]
    occurred_at: Annotated[Timestamp, Field(alias="occurredAt")]
    workspace_id: Annotated[Uuid, Field(alias="workspaceId")]
    actor: Actor
    subject: DomainEventSubject
    correlation_id: Annotated[
        Uuid,
        Field(alias="correlationId", description="Run or request that this event belongs to."),
    ]
    payload: dict[str, Any]
    project_id: Annotated[Uuid | None, Field(default=None, alias="projectId")] = None
    causation_id: Annotated[
        Uuid | None,
        Field(
            default=None,
            alias="causationId",
            description="Event or command that caused this one.",
        ),
    ] = None
    traceparent: Annotated[
        str | None,
        Field(
            default=None,
            pattern=r"^00-[0-9a-f]{32}-[0-9a-f]{16}-[0-9a-f]{2}$",
        ),
    ] = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_nulls(cls, data: Any) -> Any:
        return reject_explicit_null_keys(data, DOMAIN_OPTIONAL_FIELDS)

    @model_validator(mode="after")
    def validate_payload_for_type(self) -> Self:
        expected = _TYPED_PAYLOAD.get(self.type)
        if expected is not None:
            expected.model_validate(self.payload)
        return self


DOMAIN_DEF_MODELS: dict[str, type] = {
    "EventType": EventType,
    "ProductionState": ProductionState,
    "ProjectStateChanged": ProjectStateChanged,
    "Gate": Gate,
    "ApprovalRecorded": ApprovalRecorded,
    "ApprovalInvalidated": ApprovalInvalidated,
    "TaskAttempt": TaskAttempt,
    "BudgetChange": BudgetChange,
    "RenderCompleted": RenderCompleted,
    "RevisionApplied": RevisionApplied,
    "PublicationRecorded": PublicationRecorded,
    "PolicyVersions": PolicyVersions,
}


def domain_payload_schema_ref(model: type) -> str:
    if model is WorkflowRequest:
        return "workflow-request.schema.json"
    for def_name, def_model in DOMAIN_DEF_MODELS.items():
        if def_model is model:
            return f"#/$defs/{def_name}"
    msg = f"no schema ref for payload model {model!r}"
    raise ValueError(msg)


def domain_payload_dispatch_rules() -> list[tuple[list[str], str]]:
    type_order = {member.value: index for index, member in enumerate(EventType)}
    groups: dict[type, list[str]] = {}
    for event_type, model in _TYPED_PAYLOAD.items():
        groups.setdefault(model, []).append(event_type.value)
    rules = [
        (
            sorted(types, key=lambda value: type_order[value]),
            domain_payload_schema_ref(model),
        )
        for model, types in groups.items()
    ]
    rules.sort(key=lambda item: type_order[item[0][0]])
    return rules
