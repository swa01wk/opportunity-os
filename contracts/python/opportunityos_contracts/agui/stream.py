"""AG-UI project stream definitions (agui/stream.json $defs and x-agui block)."""

from enum import StrEnum
from typing import Annotated, Any, Final

from pydantic import ConfigDict, Field, StringConstraints, model_validator

from opportunityos_contracts._schema import ContractModel
from opportunityos_contracts.common import Uuid
from opportunityos_contracts.events.domain_event import Gate, ProductionState
from opportunityos_contracts.validators import JsonInt, reject_explicit_null_keys

AGUI_STREAM_TITLE = "AG-UI project event stream"
AGUI_STREAM_DESCRIPTION = (
    "How GET /projects/{projectId}/events encodes run progress and domain events as AG-UI "
    "events (ADR-020, docs/architecture/AGENT_ARCHITECTURE.md). Event shapes are the pinned "
    "AG-UI SDK's (ag-ui-protocol for Python, @ag-ui/core for TypeScript); this file fixes only "
    "how OpportunityOS uses them. AG-UI events are a projection of DomainEvents and attempt "
    "spans; they carry no authority, and every command goes through the REST API."
)

STEP_NAME_PATTERN: Final = (
    r"^(research|script|storyboard|revision\.impact|demonstration|narration|"
    r"tts\.scene\.[a-z0-9_.-]+|alignment|captions|compile|"
    r"render\.clip\.scene\.[a-z0-9_.-]+|assembly|mix|qa|package_build|export_build|"
    r"budget\.reserve|budget\.settle|diagnostic\.echo|diagnostic\.validate|diagnostic\.join)$"
)

StepName = Annotated[
    str,
    StringConstraints(pattern=STEP_NAME_PATTERN),
    Field(description="Workflow step names shown in the run indicator and S-13."),
]


class ActivityType(StrEnum):
    RENDER_PROGRESS = "opportunityos.render_progress"
    RUN_PAUSED = "opportunityos.run_paused"


class SceneRenderStatus(StrEnum):
    QUEUED = "queued"
    RENDERING = "rendering"
    REUSED = "reused"
    DONE = "done"
    FAILED = "failed"


class RenderScene(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    scene_id: Annotated[str, Field(alias="sceneId")]
    status: SceneRenderStatus
    percent: Annotated[JsonInt | None, Field(default=None, ge=0, le=100)] = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_null_percent(cls, data: Any) -> Any:
        return reject_explicit_null_keys(data, frozenset({"percent"}))


class RenderProgress(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    scenes: list[RenderScene]


class RunPausedReason(StrEnum):
    BUDGET = "budget"
    AWAITING_APPROVAL = "awaiting_approval"
    MANUAL_TAKEOVER = "manual_takeover"
    CANCELLING = "cancelling"


class RunPausedUnblock(StrEnum):
    RAISE_ALLOWANCE = "raise_allowance"
    OPEN_GATE = "open_gate"
    TAKE_OVER = "take_over"
    NONE = "none"


class RunPaused(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    reason: RunPausedReason
    unblock_action: Annotated[
        RunPausedUnblock | None,
        Field(
            default=None,
            alias="unblockAction",
            description="The one Studio action that unblocks the run (R-53, R-61).",
        ),
    ] = None
    gate: Annotated[
        Gate | None,
        Field(default=None, description="Set when reason = awaiting_approval."),
    ] = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_nulls(cls, data: Any) -> Any:
        return reject_explicit_null_keys(data, frozenset({"unblockAction", "gate"}))


class AguiTool(StrEnum):
    SEARCH_SOURCES = "search_sources"
    FETCH_SOURCE = "fetch_source"
    COMPUTE_DEMONSTRATION = "compute_demonstration"
    LIST_CAPABILITIES = "list_capabilities"
    VALIDATE_SCENE_SPEC = "validate_scene_spec"


class ToolCallArgsSummary(ContractModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        json_schema_extra={
            "description": (
                "Never page text, prompts, model output, secrets or signed URLs (SECURITY TH-31)."
            ),
        },
    )

    tool: AguiTool
    domain: Annotated[
        str | None,
        Field(default=None, description="Host of a fetched URL only, e.g. example.org"),
    ] = None
    query_count: Annotated[
        JsonInt | None,
        Field(default=None, alias="queryCount", ge=0),
    ] = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_nulls(cls, data: Any) -> Any:
        return reject_explicit_null_keys(data, frozenset({"domain", "queryCount"}))


class ToolCallOutcome(StrEnum):
    OK = "ok"
    REFUSED = "refused"
    DENIED = "denied"
    FAILED = "failed"


class ToolCallReason(StrEnum):
    NOT_PERMITTED = "not_permitted"
    BUDGET = "budget"
    SSRF_GUARD = "ssrf_guard"
    NOT_IN_SEARCH_RESULTS = "not_in_search_results"
    TIMEOUT = "timeout"
    PROVIDER_ERROR = "provider_error"
    INJECTION_SUSPECTED = "injection_suspected"
    OTHER = "other"


class ToolCallResultSummary(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    outcome: ToolCallOutcome
    reason: Annotated[
        ToolCallReason | None,
        Field(
            default=None,
            description="Coded, never free text from a page or the model.",
        ),
    ] = None
    count: Annotated[JsonInt | None, Field(default=None, ge=0)] = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_nulls(cls, data: Any) -> Any:
        return reject_explicit_null_keys(data, frozenset({"reason", "count"}))


class ActiveRunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    CANCELLING = "cancelling"


class ActiveRun(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    run_id: Annotated[Uuid, Field(alias="runId")]
    workflow_type: Annotated[str, Field(alias="workflowType")]
    status: ActiveRunStatus
    current_step: Annotated[StepName | None, Field(default=None, alias="currentStep")] = None
    step_index: Annotated[JsonInt | None, Field(default=None, alias="stepIndex", ge=1)] = None
    step_count: Annotated[JsonInt | None, Field(default=None, alias="stepCount", ge=1)] = None
    paused: Annotated[RunPaused | None, Field(default=None)] = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_nulls(cls, data: Any) -> Any:
        return reject_explicit_null_keys(
            data,
            frozenset({"currentStep", "stepIndex", "stepCount", "paused"}),
        )


class Blocker(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    code: Annotated[str, Field(max_length=60)]
    unblock_action: Annotated[str, Field(alias="unblockAction", max_length=40)]


class ProjectRunState(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    project_id: Annotated[Uuid, Field(alias="projectId")]
    as_of_seq: Annotated[
        JsonInt,
        Field(
            alias="asOfSeq",
            ge=0,
            description="outbox seq this snapshot reflects; the stream continues after it.",
        ),
    ]
    active_runs: Annotated[list[ActiveRun], Field(alias="activeRuns")]
    production_state: Annotated[
        ProductionState | None,
        Field(default=None, alias="productionState"),
    ] = None
    blockers: Annotated[
        list[Blocker] | None,
        Field(
            default=None,
            description=(
                "Why the project is blocked or waiting, so the Studio can say what unblocks it."
            ),
        ),
    ] = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_nulls(cls, data: Any) -> Any:
        return reject_explicit_null_keys(data, frozenset({"productionState", "blockers"}))


AGUI_DEF_MODELS: dict[str, type] = {
    "StepName": StepName,
    "ActivityType": ActivityType,
    "RenderProgress": RenderProgress,
    "RunPaused": RunPaused,
    "ToolCallArgsSummary": ToolCallArgsSummary,
    "ToolCallResultSummary": ToolCallResultSummary,
    "ProjectRunState": ProjectRunState,
}

# x-agui block models


class AguiMappingEntry(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    source: str
    event: str
    code: str | None = None
    stepName: str | None = None
    args: str | None = None
    result: str | None = None
    activityType: str | None = None
    name: str | None = None
    value: str | None = None
    note: str | None = None


class AguiCursor(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    pattern: str
    clientRule: str
    fixtures: str


class AguiSdk(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    python: str
    typescript: str
    pin: str


class AguiStreamExtension(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    sdk: AguiSdk
    transport: str
    threadId: str
    runId: str
    runStartedBy: str
    eventsUsed: list[str]
    eventsNotUsed: list[str]
    onConnect: str
    mapping: list[AguiMappingEntry]
    cursor: AguiCursor
    auth: str
    redaction: str
    authority: str
    generativeUi: str


def agui_x_block() -> dict[str, Any]:
    """Canonical x-agui mapping block (validated data, not generated from $defs)."""

    return AguiStreamExtension.model_validate(
        {
            "sdk": {
                "python": "ag-ui-protocol",
                "typescript": "@ag-ui/core",
                "pin": (
                    "exact versions in the M0 lockfiles; upgrades are their own spec (pre-1.0)"
                ),
            },
            "transport": (
                "text/event-stream; one stream per open project; SSE id is the cursor: "
                "'<seq>' for events projected from a DomainEvent (seq = outbox_event.seq, "
                "per-workspace monotonic) and '<seq>.<n>' for events from attempt spans after "
                "that DomainEvent; Last-Event-ID resumes after it"
            ),
            "threadId": "projectId",
            "runId": "execution_run.id",
            "runStartedBy": (
                "REST command returning 202 (observe mode); the AG-UI run request is not used "
                "at R1-R2"
            ),
            "eventsUsed": [
                "RUN_STARTED",
                "RUN_FINISHED",
                "RUN_ERROR",
                "STEP_STARTED",
                "STEP_FINISHED",
                "TOOL_CALL_START",
                "TOOL_CALL_ARGS",
                "TOOL_CALL_END",
                "TOOL_CALL_RESULT",
                "ACTIVITY_SNAPSHOT",
                "ACTIVITY_DELTA",
                "STATE_SNAPSHOT",
                "CUSTOM",
            ],
            "eventsNotUsed": [
                "TEXT_MESSAGE_START",
                "TEXT_MESSAGE_CONTENT",
                "TEXT_MESSAGE_END",
                "TEXT_MESSAGE_CHUNK",
                "TOOL_CALL_CHUNK",
                "STATE_DELTA",
                "MESSAGES_SNAPSHOT",
                "RAW",
                "reasoning and sub-agent events",
            ],
            "onConnect": (
                "STATE_SNAPSHOT first (schema #/$defs/ProjectRunState), "
                "then events after the cursor"
            ),
            "mapping": [
                {
                    "source": "run.state_changed to running",
                    "event": "RUN_STARTED",
                },
                {
                    "source": "run.state_changed to succeeded",
                    "event": "RUN_FINISHED",
                },
                {
                    "source": "run.state_changed to failed, or run.cancelled",
                    "event": "RUN_ERROR",
                    "code": "#/$defs/RunErrorCode",
                },
                {
                    "source": "workflow step or task_attempt.started / task_attempt.finished",
                    "event": "STEP_STARTED / STEP_FINISHED",
                    "stepName": "#/$defs/StepName",
                },
                {
                    "source": "agent tool call inside a task attempt",
                    "event": "TOOL_CALL_START, TOOL_CALL_ARGS, TOOL_CALL_END, TOOL_CALL_RESULT",
                    "args": "#/$defs/ToolCallArgsSummary",
                    "result": "#/$defs/ToolCallResultSummary",
                },
                {
                    "source": (
                        "render progress; run paused for budget, waiting for a gate, or taken over"
                    ),
                    "event": "ACTIVITY_SNAPSHOT / ACTIVITY_DELTA",
                    "activityType": "#/$defs/ActivityType",
                },
                {
                    "source": "every DomainEvent",
                    "event": "CUSTOM",
                    "name": "opportunityos.<DomainEvent.type>",
                    "value": "../events/domain-event.schema.json",
                },
                {
                    "source": (
                        "agent result stored (task_attempt.finished succeeded) and its "
                        "version-created DomainEvent"
                    ),
                    "event": (
                        "STEP_FINISHED then CUSTOM "
                        "opportunityos.<script|storyboard>.version_created"
                    ),
                    "note": "the draft awaits its gate; no AG-UI event can approve it",
                },
            ],
            "cursor": {
                "pattern": "^[0-9]+(\\.[0-9]+)?$",
                "clientRule": (
                    "apply events in cursor order; drop any cursor at or below the last applied; "
                    "on a gap in <seq>, reconnect (a reconnect always starts with STATE_SNAPSHOT)"
                ),
                "fixtures": (
                    "examples/agui/*.stream.jsonl hold one SSE frame per line as {seq, data}"
                ),
            },
            "auth": (
                "Bearer token checked on connect, scoped to workspace and project like every route "
                "(SECURITY TH-32). The server closes the stream when the token expires; the client "
                "reconnects with the refreshed token and Last-Event-ID."
            ),
            "redaction": (
                "Events carry summaries and IDs only: no page text, prompts, "
                "model output, secrets, signed URLs or email addresses (SECURITY TH-31). "
                "Full payloads are read through authorised API routes."
            ),
            "authority": (
                "None. Approve, return, cancel, retry, resume, take over, redraft and raise budget "
                "are REST commands with If-Match and the version hash. After an event the Studio "
                "re-reads what it shows."
            ),
            "generativeUi": (
                "Not used at R1-R2: the Studio renders fixed components; agents cannot request UI."
            ),
        }
    ).model_dump(by_alias=True, exclude_none=True)
