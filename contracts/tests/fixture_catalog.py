"""Fixture list shared by Python and TypeScript dual-runtime tests (SPEC-03a-03b)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = REPO_ROOT / "docs" / "contracts" / "examples"
INVALID_MANIFEST = EXAMPLES / "invalid" / "manifest.json"
AGUI_DIR = EXAMPLES / "agui"

WORKFLOW_CONTRACT = "events/workflow-request.schema.json"
DOMAIN_EVENT_CONTRACT = "events/domain-event.schema.json"
ANALYTICS_CONTRACT = "analytics/events.schema.json"
AGUI_CONTRACT = "agui/stream.json"

REGISTERED_CONTRACTS = (
    WORKFLOW_CONTRACT,
    DOMAIN_EVENT_CONTRACT,
    ANALYTICS_CONTRACT,
    AGUI_CONTRACT,
)


@dataclass(frozen=True)
class FixtureCase:
    contract: str
    file: str
    expect_valid: bool
    expected_code: str | None = None
    level: str = "schema"


@dataclass(frozen=True)
class StreamCase:
    file: str
    expect_valid: bool
    expected_code: str | None = None


def workflow_valid_examples() -> tuple[str, ...]:
    return tuple(
        sorted(path.name for path in EXAMPLES.glob("*.workflow-request.json") if path.is_file())
    )


def domain_valid_examples() -> tuple[str, ...]:
    return tuple(sorted(path.name for path in EXAMPLES.glob("*.event.json") if path.is_file()))


def analytics_valid_examples() -> tuple[str, ...]:
    return tuple(
        sorted(path.name for path in EXAMPLES.glob("*.analytics-event.json") if path.is_file())
    )


def agui_stream_examples() -> tuple[str, ...]:
    return tuple(sorted(path.name for path in AGUI_DIR.glob("*.stream.jsonl") if path.is_file()))


def load_fixture_cases() -> list[FixtureCase]:
    manifest = json.loads(INVALID_MANIFEST.read_text(encoding="utf-8"))
    cases: list[FixtureCase] = []

    for name in workflow_valid_examples():
        cases.append(FixtureCase(contract=WORKFLOW_CONTRACT, file=name, expect_valid=True))
    for name in domain_valid_examples():
        cases.append(FixtureCase(contract=DOMAIN_EVENT_CONTRACT, file=name, expect_valid=True))
    for name in analytics_valid_examples():
        cases.append(FixtureCase(contract=ANALYTICS_CONTRACT, file=name, expect_valid=True))

    for entry in manifest["fixtures"]:
        level = entry.get("level", "schema")
        if level == "stream":
            continue
        contract = entry["contract"]
        if contract not in REGISTERED_CONTRACTS:
            continue
        cases.append(
            FixtureCase(
                contract=contract,
                file=f"invalid/{entry['file']}",
                expect_valid=False,
                expected_code=entry["expected"],
                level=level,
            )
        )
    return cases


def load_stream_cases() -> list[StreamCase]:
    manifest = json.loads(INVALID_MANIFEST.read_text(encoding="utf-8"))
    cases: list[StreamCase] = [
        StreamCase(file=f"agui/{name}", expect_valid=True) for name in agui_stream_examples()
    ]
    for entry in manifest["fixtures"]:
        if entry.get("level") != "stream":
            continue
        if entry.get("contract") != AGUI_CONTRACT:
            continue
        cases.append(
            StreamCase(
                file=f"invalid/{entry['file']}",
                expect_valid=False,
                expected_code=entry["expected"],
            )
        )
    return cases
