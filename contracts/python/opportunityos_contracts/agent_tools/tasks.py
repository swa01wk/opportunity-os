"""tasks.json manifest (bounded agent tasks, R-63)."""

from typing import Annotated, Any, Literal, Self

from pydantic import ConfigDict, Field, model_validator

from opportunityos_contracts._schema import ContractModel
from opportunityos_contracts.agent_tools.execution import OutputDisposition, ReviewGate, TaskType
from opportunityos_contracts.validators import JsonInt


class TaskBudget(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    max_model_calls: Annotated[JsonInt, Field(alias="maxModelCalls", ge=0)]
    max_tool_calls: Annotated[JsonInt, Field(alias="maxToolCalls", ge=0)]
    max_input_tokens: Annotated[JsonInt, Field(alias="maxInputTokens", ge=0)]
    max_output_tokens: Annotated[JsonInt, Field(alias="maxOutputTokens", ge=0)]
    max_link_hops: Annotated[JsonInt | None, Field(default=None, alias="maxLinkHops", ge=0)] = None
    max_children: Annotated[Literal[0], Field(alias="maxChildren")]


class TaskDefinition(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    task_type: Annotated[TaskType, Field(alias="taskType")]
    input_schema: Annotated[str, Field(alias="input")]
    output_schema: Annotated[str, Field(alias="output")]
    permitted_tools: Annotated[list[str], Field(alias="permittedTools")]
    budget: TaskBudget
    retry_ceiling: Annotated[JsonInt, Field(alias="retryCeiling", ge=0)]
    timeout_sec: Annotated[JsonInt, Field(alias="timeoutSec", ge=1)]
    failure_states: Annotated[list[str], Field(alias="failureStates", min_length=1)]
    postconditions: Annotated[list[str], Field(min_length=1)]
    output_disposition: Annotated[OutputDisposition, Field(alias="outputDisposition")]
    review_gate: Annotated[ReviewGate, Field(alias="reviewGate")]
    evaluation_fixtures: Annotated[
        str | None,
        Field(default=None, alias="evaluationFixtures"),
    ] = None

    @model_validator(mode="after")
    def evaluation_fixtures_for_drafts(self) -> Self:
        if (
            self.output_disposition == OutputDisposition.DRAFT_VERSION
            and not self.evaluation_fixtures
        ):
            msg = "evaluationFixtures is required when outputDisposition is draft_version"
            raise ValueError(msg)
        if self.output_disposition == OutputDisposition.ATTEMPT_ONLY and self.evaluation_fixtures:
            msg = "evaluationFixtures must be omitted when outputDisposition is attempt_only"
            raise ValueError(msg)
        if self.budget.max_children != 0:
            msg = "maxChildren must be 0"
            raise ValueError(msg)
        return self


class TasksManifest(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    contract_version: Annotated[str, Field(alias="contractVersion")]
    tasks: Annotated[list[TaskDefinition], Field(min_length=1)]

    @model_validator(mode="before")
    @classmethod
    def allow_comment(cls, data: Any) -> Any:
        if isinstance(data, dict) and "$comment" in data:
            data = {key: value for key, value in data.items() if key != "$comment"}
        return data
