"""Fixture list shared by Python and TypeScript dual-runtime tests (SPEC-03a)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = REPO_ROOT / "docs" / "contracts" / "examples"
INVALID_MANIFEST = EXAMPLES / "invalid" / "manifest.json"
CATALOG_PATH = Path(__file__).resolve().parent / "fixture_catalog.json"

WORKFLOW_CONTRACT = "events/workflow-request.schema.json"


@dataclass(frozen=True)
class FixtureCase:
    contract: str
    file: str
    expect_valid: bool
    expected_code: str | None = None


def workflow_valid_examples() -> tuple[str, ...]:
    return tuple(
        sorted(path.name for path in EXAMPLES.glob("*.workflow-request.json") if path.is_file())
    )


def load_fixture_cases() -> list[FixtureCase]:
    manifest = json.loads(INVALID_MANIFEST.read_text(encoding="utf-8"))
    cases: list[FixtureCase] = [
        FixtureCase(contract=WORKFLOW_CONTRACT, file=name, expect_valid=True)
        for name in workflow_valid_examples()
    ]
    for entry in manifest["fixtures"]:
        if entry.get("level") != "schema":
            continue
        if entry["contract"] != WORKFLOW_CONTRACT:
            continue
        cases.append(
            FixtureCase(
                contract=entry["contract"],
                file=f"invalid/{entry['file']}",
                expect_valid=False,
                expected_code=entry["expected"],
            )
        )
    return cases


def write_catalog() -> None:
    """Emit the JSON catalog consumed by the TypeScript harness."""
    payload = [
        {
            "contract": case.contract,
            "file": case.file,
            "expectValid": case.expect_valid,
            "expectedCode": case.expected_code,
        }
        for case in load_fixture_cases()
    ]
    CATALOG_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
