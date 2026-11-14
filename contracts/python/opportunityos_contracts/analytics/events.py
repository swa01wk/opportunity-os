"""AnalyticsEvent (analytics/events.schema.json)."""

from enum import StrEnum
from typing import Annotated, Any, Final, Self

from pydantic import ConfigDict, Field, model_validator

from opportunityos_contracts._schema import ContractModel
from opportunityos_contracts.common import Sha256, Timestamp, Uuid
from opportunityos_contracts.validators import JsonInt, reject_explicit_null_keys

ANALYTICS_OPTIONAL_FIELDS: Final = frozenset({"projectId", "memberId"})


class AnalyticsEventName(StrEnum):
    VIDEO_APPROVED = "video.approved"
    VIDEO_PUBLISHED = "video.published"
    GATE_APPROVED = "gate.approved"
    RUN_FINISHED = "run.finished"
    EFFORT_LOGGED = "effort.logged"
    KPI_BASELINE_RECORDED = "kpi.baseline_recorded"
    COST_SETTLED = "cost.settled"
    RUBRIC_SCORED = "rubric.scored"
    FINDING_RESOLVED = "finding.resolved"
    METRIC_RECORDED = "metric.recorded"


class Series(StrEnum):
    WHAT_IF = "what_if"
    WAIT_HOW = "wait_how_does_that_work"
    SOLVE_THIS = "solve_this"
    INSIDE_THE_MACHINE = "inside_the_machine"


class VideoApprovedProperties(ContractModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        json_schema_extra={"x-kpis": ["KPI-01", "KPI-02", "KPI-03", "KPI-05"]},
    )

    project_id: Annotated[Uuid, Field(alias="projectId")]
    series: Series
    package_version_id: Annotated[Uuid, Field(alias="packageVersionId")]
    package_sha256: Annotated[Sha256, Field(alias="packageSha256")]
    minutes_since_gate_a: Annotated[
        JsonInt | None,
        Field(default=None, alias="minutesSinceGateA", ge=0),
    ] = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_null_minutes(cls, data: Any) -> Any:
        return reject_explicit_null_keys(data, frozenset({"minutesSinceGateA"}))


class PublicationRoute(StrEnum):
    MANUAL = "manual"
    CONNECTED = "connected"


class Platform(StrEnum):
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"


class Verification(StrEnum):
    NOT_CHECKED = "NOT_CHECKED"
    PASSED = "PASSED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


class GateLabel(StrEnum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"


class Responsibility(StrEnum):
    OWNER = "owner"
    EDITOR = "editor"
    REVIEWER = "reviewer"
    PUBLISHER = "publisher"
    ANALYST = "analyst"


class RunOutcome(StrEnum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EffortActivity(StrEnum):
    BRIEF = "brief"
    RESEARCH_REVIEW = "research_review"
    SCRIPT = "script"
    STORYBOARD = "storyboard"
    NARRATION = "narration"
    REVIEW = "review"
    REVISION = "revision"
    PACKAGING = "packaging"
    PUBLISHING = "publishing"
    CODE_REPAIR = "code_repair"
    OTHER = "other"


class KpiId(StrEnum):
    KPI_04 = "KPI-04"


class AttemptOutcome(StrEnum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REVISED = "revised"


class MetricAvailability(StrEnum):
    AVAILABLE = "available"
    MISSING = "missing"
    DELAYED = "delayed"
    UNSUPPORTED = "unsupported"
    PERMISSION_DENIED = "permission_denied"


class MetricSource(StrEnum):
    MANUAL = "manual"
    API = "api"


class VideoPublishedProperties(ContractModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        json_schema_extra={"x-kpis": ["KPI-01"]},
    )

    project_id: Annotated[Uuid, Field(alias="projectId")]
    series: Series
    publication_id: Annotated[Uuid, Field(alias="publicationId")]
    route: PublicationRoute
    platform: Platform
    verification: Verification
    package_match: Annotated[bool, Field(alias="packageMatch")]


class GateApprovedProperties(ContractModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        json_schema_extra={"x-kpis": ["KPI-04 context"]},
    )

    gate: GateLabel
    responsibility: Responsibility
    target_type: Annotated[str, Field(alias="targetType", max_length=40)]
    target_version: Annotated[JsonInt, Field(alias="targetVersion", ge=1)]
    reopened_count: Annotated[
        JsonInt | None,
        Field(default=None, alias="reopenedCount", ge=0),
    ] = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_null_reopened(cls, data: Any) -> Any:
        return reject_explicit_null_keys(data, frozenset({"reopenedCount"}))


class RunFinishedProperties(ContractModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        json_schema_extra={"x-kpis": ["KPI-02"]},
    )

    run_id: Annotated[Uuid, Field(alias="runId")]
    workflow_type: Annotated[str, Field(alias="workflowType", max_length=40)]
    outcome: RunOutcome
    attempts: Annotated[JsonInt, Field(ge=0)]
    code_repair_needed: Annotated[bool, Field(alias="codeRepairNeeded")]
    manual_takeover: Annotated[bool, Field(alias="manualTakeover")]


class EffortLoggedProperties(ContractModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        json_schema_extra={"x-kpis": ["KPI-02", "KPI-04"]},
    )

    activity: EffortActivity
    minutes: Annotated[JsonInt, Field(ge=0, le=1440)]


class KpiBaselineRecordedProperties(ContractModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        json_schema_extra={"x-kpis": ["KPI-04"]},
    )

    kpi: KpiId
    minutes: Annotated[JsonInt, Field(ge=1)]
    revisions: Annotated[JsonInt | None, Field(default=None, ge=0)] = None
    cost_minor: Annotated[JsonInt | None, Field(default=None, alias="costMinor", ge=0)] = None
    currency: Annotated[
        str | None,
        Field(default=None, pattern=r"^[A-Z]{3}$"),
    ] = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_nulls(cls, data: Any) -> Any:
        return reject_explicit_null_keys(data, frozenset({"revisions", "costMinor", "currency"}))


class CostSettledProperties(ContractModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        json_schema_extra={"x-kpis": ["KPI-05"]},
    )

    provider: Annotated[str, Field(max_length=40)]
    stage: Annotated[str, Field(max_length=40)]
    attempt_outcome: Annotated[AttemptOutcome, Field(alias="attemptOutcome")]
    estimated_minor: Annotated[JsonInt, Field(alias="estimatedMinor", ge=0)]
    actual_minor: Annotated[JsonInt, Field(alias="actualMinor", ge=0)]
    currency: Annotated[str, Field(pattern=r"^[A-Z]{3}$")]
    fx_rate: Annotated[float | None, Field(default=None, alias="fxRate", gt=0)] = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_null_fx(cls, data: Any) -> Any:
        return reject_explicit_null_keys(data, frozenset({"fxRate"}))


class RubricScoredProperties(ContractModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        json_schema_extra={"x-kpis": ["KPI-03", "KPI-14"]},
    )

    render_id: Annotated[Uuid, Field(alias="renderId")]
    correctness: Annotated[JsonInt, Field(ge=1, le=5)]
    clarity: Annotated[JsonInt, Field(ge=1, le=5)]
    originality: Annotated[JsonInt, Field(ge=1, le=5)]
    readability: Annotated[JsonInt, Field(ge=1, le=5)]
    promise_payoff: Annotated[JsonInt, Field(alias="promisePayoff", ge=1, le=5)]
    muted_review_passed: Annotated[bool, Field(alias="mutedReviewPassed")]
    all_at_least_threshold: Annotated[bool, Field(alias="allAtLeastThreshold")]


class FindingResolvedProperties(ContractModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        json_schema_extra={"x-kpis": ["KPI-03"]},
    )

    severity: Annotated[str, Field(max_length=20)]
    material: bool
    disposition: Annotated[str, Field(max_length=40)]


class MetricRecordedProperties(ContractModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        json_schema_extra={
            "x-kpis": [
                "KPI-06",
                "KPI-07",
                "KPI-08",
                "KPI-09",
                "KPI-10",
                "KPI-11",
                "KPI-13",
            ]
        },
    )

    publication_id: Annotated[Uuid, Field(alias="publicationId")]
    measure: Annotated[str, Field(max_length=80)]
    value: float | None = None
    availability: MetricAvailability
    window_start: Annotated[Timestamp, Field(alias="windowStart")]
    window_end: Annotated[Timestamp, Field(alias="windowEnd")]
    source: MetricSource
    cold_start: Annotated[bool, Field(alias="coldStart")]
    denominator: Annotated[str | None, Field(default=None, max_length=80)] = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_null_denominator(cls, data: Any) -> Any:
        return reject_explicit_null_keys(data, frozenset({"denominator"}))


_PROPERTY_MODELS: dict[AnalyticsEventName, type[ContractModel]] = {
    AnalyticsEventName.VIDEO_APPROVED: VideoApprovedProperties,
    AnalyticsEventName.VIDEO_PUBLISHED: VideoPublishedProperties,
    AnalyticsEventName.GATE_APPROVED: GateApprovedProperties,
    AnalyticsEventName.RUN_FINISHED: RunFinishedProperties,
    AnalyticsEventName.EFFORT_LOGGED: EffortLoggedProperties,
    AnalyticsEventName.KPI_BASELINE_RECORDED: KpiBaselineRecordedProperties,
    AnalyticsEventName.COST_SETTLED: CostSettledProperties,
    AnalyticsEventName.RUBRIC_SCORED: RubricScoredProperties,
    AnalyticsEventName.FINDING_RESOLVED: FindingResolvedProperties,
    AnalyticsEventName.METRIC_RECORDED: MetricRecordedProperties,
}


class AnalyticsEvent(ContractModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    source_event_id: Annotated[Uuid, Field(alias="sourceEventId")]
    event_name: Annotated[AnalyticsEventName, Field(alias="eventName")]
    event_version: Annotated[JsonInt, Field(alias="eventVersion", ge=1)]
    occurred_at: Annotated[Timestamp, Field(alias="occurredAt")]
    workspace_id: Annotated[Uuid, Field(alias="workspaceId")]
    properties: dict[str, Any]
    project_id: Annotated[Uuid | None, Field(default=None, alias="projectId")] = None
    member_id: Annotated[Uuid | None, Field(default=None, alias="memberId")] = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_nulls(cls, data: Any) -> Any:
        return reject_explicit_null_keys(data, ANALYTICS_OPTIONAL_FIELDS)

    @model_validator(mode="after")
    def validate_properties_for_name(self) -> Self:
        expected = _PROPERTY_MODELS.get(self.event_name)
        if expected is not None:
            expected.model_validate(self.properties)
        return self


ANALYTICS_DEF_MODELS: dict[str, type] = {
    "video_approved": VideoApprovedProperties,
    "video_published": VideoPublishedProperties,
    "gate_approved": GateApprovedProperties,
    "run_finished": RunFinishedProperties,
    "effort_logged": EffortLoggedProperties,
    "kpi_baseline_recorded": KpiBaselineRecordedProperties,
    "cost_settled": CostSettledProperties,
    "rubric_scored": RubricScoredProperties,
    "finding_resolved": FindingResolvedProperties,
    "metric_recorded": MetricRecordedProperties,
}
