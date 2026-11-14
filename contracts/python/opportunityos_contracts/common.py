"""Shared primitives referenced by every contract (common.schema.json)."""

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

Uuid = Annotated[
    str,
    StringConstraints(pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
]

Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]

Timestamp = Annotated[str, Field(description="Absolute UTC timestamp (RFC 3339).")]

SemVer = Annotated[
    str,
    StringConstraints(
        pattern=r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-[0-9A-Za-z.-]+)?$"
    ),
]

LocalId = Annotated[
    str,
    StringConstraints(pattern=r"^[a-z][a-z0-9_.-]{0,63}$"),
]

Token = Annotated[
    str,
    StringConstraints(pattern=r"^[a-z][a-z0-9]*(\.[a-z0-9]+)*$", max_length=64),
]


class Money(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount_minor: Annotated[int, Field(alias="amountMinor")]
    currency: Annotated[str, StringConstraints(pattern=r"^[A-Z]{3}$")]
    fx_rate_to_reporting: Annotated[
        str | None,
        Field(default=None, alias="fxRateToReporting"),
    ] = None


class VersionRef(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: Uuid
    version: Annotated[int, Field(ge=1)]
    sha256: Sha256


class BlobRef(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    key: Annotated[
        str,
        StringConstraints(pattern=r"^ws/[0-9a-f-]{36}/sha256/[0-9a-f]{64}\.[a-z0-9]{1,8}$"),
    ]
    sha256: Sha256
    bytes: Annotated[int, Field(ge=0)]
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


class Actor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: ActorType
    id: Annotated[str, Field(max_length=100)]
    responsibility: Responsibility | None = None


class ErrorClass(StrEnum):
    RETRYABLE_PROVIDER = "retryable_provider"
    INVALID_CONTENT = "invalid_content"
    RENDER_DEFECT = "render_defect"
    UNCERTAIN_EXTERNAL = "uncertain_external"
    RESOURCE_LIMIT = "resource_limit"
    AUTHORIZATION = "authorization"
    CONFLICT = "conflict"
    INTERNAL = "internal"


class ErrorTarget(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scene_id: Annotated[LocalId | None, Field(default=None, alias="sceneId")] = None
    object_id: Annotated[LocalId | None, Field(default=None, alias="objectId")] = None
    claim_id: Annotated[Uuid | None, Field(default=None, alias="claimId")] = None
    asset_id: Annotated[Uuid | None, Field(default=None, alias="assetId")] = None
    account_label: Annotated[
        str | None,
        Field(default=None, alias="accountLabel", max_length=100),
    ] = None
    field: Annotated[str | None, Field(default=None, max_length=200)] = None


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
