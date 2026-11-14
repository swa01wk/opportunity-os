"""T-33 contract codegen, drift and equivalence (SPEC-03a-03b)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from schema_compare import schema_diff

from opportunityos_contracts._build import generate

REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINES = Path(__file__).resolve().parent / "baselines"
COMMITTED_COMMON = REPO_ROOT / "docs" / "contracts" / "common.schema.json"
COMMITTED_WORKFLOW = REPO_ROOT / "docs" / "contracts/events/workflow-request.schema.json"
COMMITTED_DOMAIN = REPO_ROOT / "docs/contracts/events/domain-event.schema.json"
COMMITTED_AGUI = REPO_ROOT / "docs/contracts/agui/stream.json"
COMMITTED_ANALYTICS = REPO_ROOT / "docs/contracts/analytics/events.schema.json"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _generated_paths(root: Path) -> tuple[Path, ...]:
    return (
        root / "docs/contracts/common.schema.json",
        root / "docs/contracts/events/workflow-request.schema.json",
        root / "docs/contracts/events/domain-event.schema.json",
        root / "docs/contracts/agui/stream.json",
        root / "docs/contracts/analytics/events.schema.json",
    )


AC3_ALLOWED_COMMON_DIFFS = frozenset({"missing in expected: $defs.Timestamp.pattern"})


@pytest.mark.t("T-33")
def test_contracts_is_idempotent(tmp_path: Path) -> None:
    generate(tmp_path)
    paths = _generated_paths(tmp_path)
    before = tuple(path.read_bytes() for path in paths)
    generate(tmp_path)
    after = tuple(path.read_bytes() for path in paths)
    assert before == after


@pytest.mark.t("T-33")
def test_generated_schemas_match_committed_files(tmp_path: Path) -> None:
    generate(tmp_path)
    common, workflow, domain, agui, analytics = _generated_paths(tmp_path)
    assert common.read_bytes() == COMMITTED_COMMON.read_bytes()
    assert workflow.read_bytes() == COMMITTED_WORKFLOW.read_bytes()
    assert domain.read_bytes() == COMMITTED_DOMAIN.read_bytes()
    assert agui.read_bytes() == COMMITTED_AGUI.read_bytes()
    assert analytics.read_bytes() == COMMITTED_ANALYTICS.read_bytes()


@pytest.mark.t("T-33")
def test_common_schema_matches_stage_2a_baseline(tmp_path: Path) -> None:
    generate(tmp_path)
    expected = _load_json(BASELINES / "common.stage2a.json")
    actual = _load_json(_generated_paths(tmp_path)[0])
    diff = schema_diff(expected, actual)
    assert set(diff) == AC3_ALLOWED_COMMON_DIFFS, "\n".join(diff[:20])


@pytest.mark.t("T-33")
def test_workflow_schema_matches_040_except_diagnostic(tmp_path: Path) -> None:
    generate(tmp_path)
    expected = _load_json(BASELINES / "workflow-request.0.4.0.json")
    actual = _load_json(_generated_paths(tmp_path)[1])
    expected_types = list(expected["properties"]["workflowType"]["enum"])
    actual_types = list(actual["properties"]["workflowType"]["enum"])
    assert actual_types == [*expected_types, "diagnostic"]
    expected["properties"]["workflowType"]["enum"] = actual_types
    diff = schema_diff(expected, actual)
    assert not diff, "\n".join(diff[:20])


@pytest.mark.t("T-33")
def test_domain_event_schema_matches_040_baseline(tmp_path: Path) -> None:
    generate(tmp_path)
    expected = _load_json(BASELINES / "domain-event.0.4.0.json")
    actual = _load_json(_generated_paths(tmp_path)[2])
    diff = schema_diff(expected, actual)
    assert not diff, "\n".join(diff[:20])


@pytest.mark.t("T-33")
def test_analytics_schema_matches_020_baseline(tmp_path: Path) -> None:
    generate(tmp_path)
    expected = _load_json(BASELINES / "analytics.0.2.0.json")
    actual = _load_json(_generated_paths(tmp_path)[4])
    diff = schema_diff(expected, actual)
    assert not diff, "\n".join(diff[:20])


@pytest.mark.t("T-33")
def test_agui_stream_matches_040_except_diagnostic_step_names(tmp_path: Path) -> None:
    generate(tmp_path)
    expected = _load_json(BASELINES / "stream.0.4.0.json")
    actual = _load_json(_generated_paths(tmp_path)[3])
    expected_pattern = expected["$defs"]["StepName"]["pattern"]
    actual_pattern = actual["$defs"]["StepName"]["pattern"]
    assert r"diagnostic\.echo" in actual_pattern
    assert actual_pattern != expected_pattern
    expected["$defs"]["StepName"]["pattern"] = actual_pattern
    diff = schema_diff(expected, actual)
    assert not diff, "\n".join(diff[:20])
