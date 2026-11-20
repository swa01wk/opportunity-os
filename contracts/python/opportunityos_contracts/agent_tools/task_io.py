"""Task input and output shapes (task-io.schema.json)."""

from typing import Annotated

from pydantic import ConfigDict, Field, StringConstraints

from opportunityos_contracts._schema import ContractModel
from opportunityos_contracts.common import Uuid

# Baseline task-io defs (research, script, storyboard) are carried from the 0.4.0 schema
# document; only diagnostic_echo adds Pydantic models in this spec (A-43).


class RevisionScope(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    revision_id: Annotated[Uuid, Field(alias="revisionId")]
    target_ids: Annotated[list[str], Field(alias="targetIds", min_length=1, max_length=12)]


class DiagnosticEchoInput(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    text: Annotated[
        str,
        StringConstraints(min_length=1, max_length=200),
        Field(description="Synthetic diagnostic string (A-43)."),
    ]


class DiagnosticEchoOutput(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    text: Annotated[str, StringConstraints(min_length=1, max_length=200)]
    model_id: Annotated[
        str,
        StringConstraints(min_length=1, max_length=120),
        Field(alias="modelId"),
    ]


# Registry entry for schema export (SPEC-03c).
TASK_IO_DEF_MODELS: dict[str, type[ContractModel]] = {
    "DiagnosticEchoInput": DiagnosticEchoInput,
    "DiagnosticEchoOutput": DiagnosticEchoOutput,
}
