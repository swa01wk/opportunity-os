"""Execution contract types (execution.schema.json)."""

from enum import StrEnum
from typing import Annotated, Any, Literal, Self

from pydantic import ConfigDict, Field, model_validator

from opportunityos_contracts._schema import ContractModel
from opportunityos_contracts.agent_tools.task_io import RevisionScope
from opportunityos_contracts.common import (
    ErrorClass,
    Money,
    SemVer,
    Sha256,
    Timestamp,
    Uuid,
    VersionRef,
)
from opportunityos_contracts.validators import JsonBool, JsonInt, reject_explicit_null_keys

EXECUTION_OPTIONAL_FIELDS = frozenset(
    {
        "output",
        "evidence",
        "failure",
        "errorClass",
        "promptSha256",
        "revisionScope",
        "untrustedSources",
    }
)


class TaskType(StrEnum):
    RESEARCH = "research"
    SCRIPT = "script"
    STORYBOARD = "storyboard"
    DIAGNOSTIC_ECHO = "diagnostic_echo"


class OutputDisposition(StrEnum):
    DRAFT_VERSION = "draft_version"
    ATTEMPT_ONLY = "attempt_only"


class ReviewGate(StrEnum):
    CLAIM_REVIEW = "claim_review"
    B_EXPLANATION_SCRIPT = "B_explanation_script"
    C_STORYBOARD = "C_storyboard"
    NONE = "none"


class FailureState(StrEnum):
    SCHEMA_INVALID = "schema_invalid"
    STALE_INPUT = "stale_input"
    CITATION_INVALID = "citation_invalid"
    UNKNOWN_CLAIM_REFERENCE = "unknown_claim_reference"
    SPEC_INVALID = "spec_invalid"
    CAPABILITY_GAP = "capability_gap"
    OUT_OF_SCOPE_CHANGE = "out_of_scope_change"
    BUDGET_EXHAUSTED = "budget_exhausted"
    TIMED_OUT = "timed_out"
    PROVIDER_ERROR = "provider_error"
    INJECTION_DETECTED = "injection_detected"
    CANCELLED = "cancelled"


class InputRole(StrEnum):
    BRIEF = "brief"
    CLAIMS = "claims"
    DEMONSTRATION = "demonstration"
    SCRIPT = "script"
    STORYBOARD = "storyboard"
    CAPABILITIES = "capabilities"
    BRAND_KIT = "brand_kit"
    REVISION_NOTE = "revision_note"


class DataClassification(StrEnum):
    INTERNAL = "internal"
    PUBLIC_SOURCES = "public_sources"


class PermittedTool(StrEnum):
    SEARCH_SOURCES = "search_sources"
    FETCH_SOURCE = "fetch_source"
    COMPUTE_DEMONSTRATION = "compute_demonstration"
    LIST_CAPABILITIES = "list_capabilities"
    VALIDATE_SCENE_SPEC = "validate_scene_spec"


class InputBinding(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    role: InputRole
    ref: VersionRef


class AttemptBudget(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    max_model_calls: Annotated[JsonInt, Field(alias="maxModelCalls", ge=0)]
    max_tool_calls: Annotated[JsonInt, Field(alias="maxToolCalls", ge=0)]
    max_input_tokens: Annotated[JsonInt, Field(alias="maxInputTokens", ge=0)]
    max_output_tokens: Annotated[JsonInt, Field(alias="maxOutputTokens", ge=0)]
    timeout_sec: Annotated[JsonInt, Field(alias="timeoutSec", ge=1)]
    retry_ceiling: Annotated[JsonInt, Field(alias="retryCeiling", ge=0)]
    max_children: Annotated[Literal[0], Field(alias="maxChildren")]
    reserved: Money


class TaskContract(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    contract_version: Annotated[SemVer, Field(alias="contractVersion")]
    task_type: Annotated[TaskType, Field(alias="taskType")]
    workspace_id: Annotated[Uuid, Field(alias="workspaceId")]
    project_id: Annotated[Uuid, Field(alias="projectId")]
    run_id: Annotated[Uuid, Field(alias="runId")]
    attempt_id: Annotated[Uuid, Field(alias="attemptId")]
    attempt: Annotated[JsonInt, Field(ge=1)]
    idempotency_key: Annotated[str, Field(alias="idempotencyKey", max_length=200)]
    objective: Annotated[str, Field(max_length=300)]
    inputs: Annotated[list[InputBinding], Field(min_length=1)]
    permitted_tools: Annotated[list[PermittedTool], Field(alias="permittedTools")]
    budget: AttemptBudget
    data_classification: Annotated[DataClassification, Field(alias="dataClassification")]
    output_disposition: Annotated[OutputDisposition, Field(alias="outputDisposition")]
    review_gate: Annotated[ReviewGate, Field(alias="reviewGate")]
    prompt_sha256: Annotated[Sha256 | None, Field(default=None, alias="promptSha256")] = None
    revision_scope: Annotated[
        RevisionScope | None,
        Field(default=None, alias="revisionScope"),
    ] = None

    @model_validator(mode="after")
    def disposition_matches_task(self) -> Self:
        if self.task_type == TaskType.DIAGNOSTIC_ECHO:
            if self.output_disposition != OutputDisposition.ATTEMPT_ONLY:
                msg = "diagnostic_echo requires outputDisposition attempt_only"
                raise ValueError(msg)
            if self.review_gate != ReviewGate.NONE:
                msg = "diagnostic_echo requires reviewGate none"
                raise ValueError(msg)
        else:
            if self.output_disposition != OutputDisposition.DRAFT_VERSION:
                msg = "bounded tasks require outputDisposition draft_version"
                raise ValueError(msg)
            if self.review_gate == ReviewGate.NONE:
                msg = "reviewGate none is only allowed for diagnostic_echo"
                raise ValueError(msg)
        if self.budget.max_children != 0:
            msg = "maxChildren must be 0"
            raise ValueError(msg)
        return self


class ContextEnvelope(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    attempt_id: Annotated[Uuid, Field(alias="attemptId")]
    assembled_at: Annotated[Timestamp, Field(alias="assembledAt")]
    inputs: Annotated[list[InputBinding], Field(default_factory=list)]
    task_input_sha256: Annotated[Sha256, Field(alias="taskInputSha256")]
    remaining_budget: Annotated[Money, Field(alias="remainingBudget")]
    untrusted_sources: Annotated[
        JsonInt | None,
        Field(default=None, alias="untrustedSources", ge=0),
    ] = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_nulls(cls, data: Any) -> Any:
        return reject_explicit_null_keys(data, frozenset({"untrustedSources"}))


class ValidationStageName(StrEnum):
    SCHEMA = "schema"
    POLICY_FRESHNESS = "policy_freshness"
    ACCEPTANCE = "acceptance"


class ValidationStage(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    stage: ValidationStageName
    passed: JsonBool
    failure: FailureState | None = None
    detail: Annotated[str | None, Field(default=None, max_length=300)] = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_nulls(cls, data: Any) -> Any:
        return reject_explicit_null_keys(data, frozenset({"failure", "detail"}))


class AgentResultStatus(StrEnum):
    VERIFIED = "verified"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ConsumedBudget(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    model_calls: Annotated[JsonInt, Field(alias="modelCalls", ge=0)]
    tool_calls: Annotated[JsonInt, Field(alias="toolCalls", ge=0)]
    input_tokens: Annotated[JsonInt, Field(alias="inputTokens", ge=0)]
    output_tokens: Annotated[JsonInt, Field(alias="outputTokens", ge=0)]
    actual_cost: Annotated[Money | None, Field(default=None, alias="actualCost")] = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_nulls(cls, data: Any) -> Any:
        return reject_explicit_null_keys(data, frozenset({"actualCost"}))


class AgentResult(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    contract_version: Annotated[SemVer, Field(alias="contractVersion")]
    attempt_id: Annotated[Uuid, Field(alias="attemptId")]
    status: AgentResultStatus
    validation: Annotated[list[ValidationStage], Field(min_length=1, max_length=3)]
    consumed: ConsumedBudget
    proposed_actions: Annotated[list[Any], Field(alias="proposedActions", max_length=0)]
    proposed_graph_changes: Annotated[list[Any], Field(alias="proposedGraphChanges", max_length=0)]
    output: VersionRef | None = None
    evidence: Annotated[list[Uuid] | None, Field(default=None)] = None
    failure: FailureState | None = None
    error_class: Annotated[ErrorClass | None, Field(default=None, alias="errorClass")] = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_nulls(cls, data: Any) -> Any:
        return reject_explicit_null_keys(data, EXECUTION_OPTIONAL_FIELDS)


EXECUTION_DEF_MODELS: dict[str, type] = {
    "TaskType": TaskType,
    "FailureState": FailureState,
    "InputBinding": InputBinding,
    "Budget": AttemptBudget,
    "TaskContract": TaskContract,
    "ContextEnvelope": ContextEnvelope,
    "ValidationStage": ValidationStage,
    "AgentResult": AgentResult,
}
