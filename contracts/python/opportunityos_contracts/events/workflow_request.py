"""WorkflowRequest (events/workflow-request.schema.json)."""

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from opportunityos_contracts.common import Actor, LocalId, Money, Uuid, VersionRef


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


class WorkflowRequestInput(BaseModel):
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
    estimated_cost: Annotated[Money | None, Field(default=None, alias="estimatedCost")] = None


class WorkflowRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    request_id: Annotated[Uuid, Field(alias="requestId")]
    workflow_type: Annotated[WorkflowType, Field(alias="workflowType")]
    project_id: Annotated[Uuid, Field(alias="projectId")]
    requested_by: Annotated[Actor, Field(alias="requestedBy")]
    input: WorkflowRequestInput
    not_before: Annotated[str | None, Field(default=None, alias="notBefore")] = None
