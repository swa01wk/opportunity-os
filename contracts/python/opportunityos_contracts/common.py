"""Shared primitives referenced by every contract (common.schema.json)."""

from enum import StrEnum
from typing import Annotated, Any

from pydantic import ConfigDict, Field, StringConstraints, model_validator

from opportunityos_contracts._schema import ContractModel
from opportunityos_contracts.validators import (
    FX_RATE_PATTERN,
    TIMESTAMP_PATTERN,
    JsonInt,
    reject_explicit_null_keys,
)

Uuid = Annotated[
    str,
    StringConstraints(pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    Field(json_schema_extra={"format": "uuid"}),
]

Sha256 = Annotated[
    str,
    StringConstraints(pattern=r"^[0-9a-f]{64}$"),
    Field(description="Lowercase hex SHA-256 of canonical JSON (RFC 8785) or of file bytes."),
]

Timestamp = Annotated[
    str,
    StringConstraints(pattern=TIMESTAMP_PATTERN),
    Field(
        description=(
            "Absolute UTC timestamp (RFC 3339). Display timezone is a destination setting (R-04)."
        ),
        json_schema_extra={"format": "date-time"},
    ),
]

SemVer = Annotated[
    str,
    StringConstraints(
        pattern=r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-[0-9A-Za-z.-]+)?$"
    ),
]

LocalId = Annotated[
    str,
    StringConstraints(pattern=r"^[a-z][a-z0-9_.-]{0,63}$"),
    Field(
        description=(
            "Stable, human-readable ID unique within its document "
            "(objects, elements, scenes, beats, phrases)."
        ),
    ),
]

Token = Annotated[
    str,
    StringConstraints(pattern=r"^[a-z][a-z0-9]*(\.[a-z0-9]+)*$", max_length=64),
    Field(
        description=(
            "Design-token name from docs/design/tokens.md, e.g. color.layer.3 or ease.standard. "
            "Never a raw value."
        ),
    ),
]

FxRateToReporting = Annotated[
    str,
    StringConstraints(pattern=FX_RATE_PATTERN),
    Field(
        description=(
            "Recorded conversion rate into the reporting currency (INR, Q-05), as a decimal string."
        ),
    ),
]


class Money(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    amount_minor: Annotated[
        JsonInt,
        Field(alias="amountMinor", description="Amount in minor units (paise, cents)."),
    ]
    currency: Annotated[str, StringConstraints(pattern=r"^[A-Z]{3}$")]
    fx_rate_to_reporting: Annotated[
        FxRateToReporting | None,
        Field(default=None, alias="fxRateToReporting"),
    ] = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_null_fx(cls, data: Any) -> Any:
        return reject_explicit_null_keys(data, frozenset({"fxRateToReporting"}))


class VersionRef(ContractModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        json_schema_extra={
            "description": (
                "Pointer to one immutable version of a record. "
                "Approvals and manifests bind to these."
            ),
        },
    )

    id: Uuid
    version: Annotated[JsonInt, Field(ge=1)]
    sha256: Sha256


class BlobRef(ContractModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        json_schema_extra={
            "description": "Content-addressed object in private storage (ADR-007).",
        },
    )

    key: Annotated[
        str,
        StringConstraints(pattern=r"^ws/[0-9a-f-]{36}/sha256/[0-9a-f]{64}\.[a-z0-9]{1,8}$"),
    ]
    sha256: Sha256
    bytes: Annotated[JsonInt, Field(ge=0)]
    media_type: Annotated[str, Field(alias="mediaType", max_length=100)]


class ActorType(StrEnum):
    MEMBER = "member"
    SERVICE = "service"
    AGENT_TASK = "agent_task"


class Responsibility(StrEnum):
    OWNER = "owner"
    EDITOR = "editor"
    REVIEWER = "reviewer"
    PUBLISHER = "publisher"
    ANALYST = "analyst"


class ErrorClass(StrEnum):
    """R-53 classification. Each class has its own repair options."""

    RETRYABLE_PROVIDER = "retryable_provider"
    INVALID_CONTENT = "invalid_content"
    RENDER_DEFECT = "render_defect"
    UNCERTAIN_EXTERNAL = "uncertain_external"
    RESOURCE_LIMIT = "resource_limit"
    AUTHORIZATION = "authorization"
    CONFLICT = "conflict"
    INTERNAL = "internal"


class Actor(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    type: ActorType
    id: Annotated[str, Field(max_length=100)]
    responsibility: Annotated[
        Responsibility | None,
        Field(
            default=None,
            description=(
                "PRD §2.3 responsibility the action was taken under (R-05). Only members have one."
            ),
        ),
    ] = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_null_responsibility(cls, data: Any) -> Any:
        return reject_explicit_null_keys(data, frozenset({"responsibility"}))


class ErrorTarget(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    scene_id: Annotated[LocalId | None, Field(default=None, alias="sceneId")] = None
    object_id: Annotated[LocalId | None, Field(default=None, alias="objectId")] = None
    claim_id: Annotated[Uuid | None, Field(default=None, alias="claimId")] = None
    asset_id: Annotated[Uuid | None, Field(default=None, alias="assetId")] = None
    account_label: Annotated[
        str | None,
        Field(default=None, alias="accountLabel", max_length=100),
    ] = None
    field: Annotated[
        str | None,
        Field(
            default=None,
            max_length=200,
            description="JSON pointer into the failing document.",
        ),
    ] = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_nulls(cls, data: Any) -> Any:
        return reject_explicit_null_keys(
            data,
            frozenset(
                {
                    "sceneId",
                    "objectId",
                    "claimId",
                    "assetId",
                    "accountLabel",
                    "field",
                }
            ),
        )


COMMON_DEF_MODELS: dict[str, type] = {
    "Money": Money,
    "VersionRef": VersionRef,
    "BlobRef": BlobRef,
    "Actor": Actor,
    "ErrorClass": ErrorClass,
    "ErrorTarget": ErrorTarget,
}

COMMON_DEF_ALIASES: dict[str, type] = {
    "Uuid": Uuid,
    "Sha256": Sha256,
    "Timestamp": Timestamp,
    "SemVer": SemVer,
    "LocalId": LocalId,
    "Token": Token,
}
