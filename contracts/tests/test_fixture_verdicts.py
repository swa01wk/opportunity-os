"""T-33 dual-runtime fixture verdicts (SPEC-03a AC4)."""

from __future__ import annotations

import pytest
from fixture_catalog import load_fixture_cases
from fixture_harness import (
    load_fixture_payload,
    pydantic_validator,
    register_schema,
    validate_json_schema,
    validate_pydantic,
)

from opportunityos_contracts.analytics.events import AnalyticsEvent
from opportunityos_contracts.events.domain_event import DomainEvent
from opportunityos_contracts.events.workflow_request import WorkflowRequest

register_schema(
    "events/workflow-request.schema.json",
    pydantic=pydantic_validator(WorkflowRequest),
)
register_schema(
    "events/domain-event.schema.json",
    pydantic=pydantic_validator(DomainEvent),
)
register_schema(
    "analytics/events.schema.json",
    pydantic=pydantic_validator(AnalyticsEvent),
)


@pytest.mark.t("T-33")
@pytest.mark.parametrize(
    "case",
    load_fixture_cases(),
    ids=lambda case: case.file,
)
def test_pydantic_and_json_schema_agree(case) -> None:
    payload = load_fixture_payload(case)
    pydantic_ok = validate_pydantic(case.contract, payload)
    json_schema_ok = validate_json_schema(case.contract, payload)
    assert pydantic_ok == json_schema_ok
    assert pydantic_ok == case.expect_valid
    if not case.expect_valid:
        assert case.expected_code == "SCHEMA"
