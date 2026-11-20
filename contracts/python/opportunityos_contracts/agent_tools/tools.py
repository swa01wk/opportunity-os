"""Agent tool argument schemas (tools.schema.json).

Pydantic models mirror the 0.2.0 schema; generation keeps the committed baseline bytes.
"""

from enum import StrEnum
from typing import Annotated, Any

from pydantic import ConfigDict, Field, StringConstraints

from opportunityos_contracts._schema import ContractModel
from opportunityos_contracts.common import LocalId, Timestamp, Uuid
from opportunityos_contracts.validators import JsonBool, JsonInt, reject_explicit_null_keys


class SearchSourcesInput(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    query: Annotated[str, StringConstraints(min_length=2, max_length=200)]
    max_results: Annotated[JsonInt | None, Field(default=5, alias="maxResults", ge=1, le=10)] = 5


class SearchResult(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    result_id: Annotated[LocalId, Field(alias="resultId")]
    title: Annotated[str, Field(max_length=300)]
    url: Annotated[str, Field(max_length=2000)]
    snippet: Annotated[str | None, Field(default=None, max_length=500)] = None


class SearchSourcesOutput(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    results: Annotated[list[SearchResult], Field(max_length=10)]


class FetchSourceInput(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    url: Annotated[
        str,
        StringConstraints(pattern=r"^https://", max_length=2000),
        Field(json_schema_extra={"format": "uri"}),
    ]


class LinkRef(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    url: Annotated[
        str,
        StringConstraints(pattern=r"^https://", max_length=2000),
        Field(json_schema_extra={"format": "uri"}),
    ]
    text: Annotated[str | None, Field(default=None, max_length=200)] = None


class ContentType(StrEnum):
    TEXT_HTML = "text/html"
    APPLICATION_PDF = "application/pdf"
    TEXT_PLAIN = "text/plain"


class FetchSourceOutput(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    source_id: Annotated[Uuid, Field(alias="sourceId")]
    final_url: Annotated[str, Field(alias="finalUrl", max_length=2000)]
    retrieved_at: Annotated[Timestamp, Field(alias="retrievedAt")]
    content_type: Annotated[ContentType, Field(alias="contentType")]
    untrusted_text: Annotated[str, Field(alias="untrustedText", max_length=60000)]
    truncated: JsonBool
    title: Annotated[str | None, Field(default=None, max_length=300)] = None
    publisher: Annotated[str | None, Field(default=None, max_length=200)] = None
    published_at: Annotated[
        str | None,
        Field(default=None, alias="publishedAt", max_length=40),
    ] = None
    links: Annotated[list[LinkRef] | None, Field(default=None, max_length=100)] = None

    @staticmethod
    def validate_no_nulls(data: Any) -> Any:
        return reject_explicit_null_keys(
            data,
            frozenset({"title", "publisher", "publishedAt", "links"}),
        )


class ComputeDemonstrationInput(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    function: Annotated[str, StringConstraints(pattern=r"^[a-z][a-z0-9_]{2,63}$")]
    params: dict[str, Any] = Field(default_factory=dict)


class ComputeDemonstrationOutput(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    ok: JsonBool
    results: dict[str, Any] | None = None
    results_sha256: Annotated[Any | None, Field(default=None, alias="resultsSha256")] = None
    error: Annotated[str | None, Field(default=None, max_length=300)] = None


class ListCapabilitiesInput(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class ValidateSceneSpecInput(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    video_spec: Annotated[dict[str, Any], Field(alias="videoSpec")]


class ValidationErrorItem(ContractModel):
    """Placeholder; full shape lives in media render-job schema (SPEC-03d)."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class ValidateSceneSpecOutput(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    valid: JsonBool
    errors: Annotated[list[dict[str, Any]], Field(max_length=200)]
