"""WorkflowRequest (events/workflow-request.schema.json)."""

from enum import StrEnum
from typing import Annotated, Any

from pydantic import ConfigDict, Field, model_validator

from opportunityos_contracts._schema import ContractModel
from opportunityos_contracts.common import Actor, LocalId, Money, Timestamp, Uuid, VersionRef
from opportunityos_contracts.validators import reject_explicit_null_keys

OPTIONAL_WORKFLOW_INPUT_FIELDS = (
    "contractRef",
    "scriptRef",
    "storyboardRef",
    "revisionId",
    "packageRef",
    "sceneIds",
    "estimatedCost",
)


class WorkflowType(StrEnum):
    RESEARCH = "research"
    SCRIPT = "script"
    STORYBOARD = "storyboard"
    NARRATION = "narration"
    PREVIEW = "preview"
    MASTER = "master"
    REVISION = "revision"
    REVISION_REDRAFT = "revision_redraft"
    PACKAGE_BUILD = "package_build"
    EXPORT_BUILD = "export_build"
    DATA_EXPORT = "data_export"
    RETENTION_SWEEP = "retention_sweep"
    PROJECT_DELETION = "project_deletion"
    DIAGNOSTIC = "diagnostic"


class WorkflowRequestInput(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    contract_ref: Annotated[VersionRef | None, Field(default=None, alias="contractRef")] = None
    script_ref: Annotated[VersionRef | None, Field(default=None, alias="scriptRef")] = None
    storyboard_ref: Annotated[VersionRef | None, Field(default=None, alias="storyboardRef")] = None
    revision_id: Annotated[Uuid | None, Field(default=None, alias="revisionId")] = None
    package_ref: Annotated[VersionRef | None, Field(default=None, alias="packageRef")] = None
    scene_ids: Annotated[
        list[LocalId] | None,
        Field(default=None, alias="sceneIds", max_length=24),
    ] = None
    estimated_cost: Annotated[
        Money | None,
        Field(
            default=None,
            alias="estimatedCost",
            description=(
                "Run estimate checked against the remaining allowance at "
                "request time (R-07). Each task still reserves its own "
                "cost before dispatch (R-34)."
            ),
        ),
    ] = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_nulls(cls, data: Any) -> Any:
        return reject_explicit_null_keys(data, frozenset(OPTIONAL_WORKFLOW_INPUT_FIELDS))


class WorkflowRequest(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    request_id: Annotated[Uuid, Field(alias="requestId")]
    workflow_type: Annotated[WorkflowType, Field(alias="workflowType")]
    project_id: Annotated[Uuid, Field(alias="projectId")]
    requested_by: Annotated[Actor, Field(alias="requestedBy")]
    input: WorkflowRequestInput
    not_before: Annotated[Timestamp | None, Field(default=None, alias="notBefore")] = None

    @model_validator(mode="before")
    @classmethod
    def validate_not_before_not_null(cls, data: Any) -> Any:
        return reject_explicit_null_keys(data, frozenset({"notBefore"}))
