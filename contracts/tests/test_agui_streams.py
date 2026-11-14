"""T-33 recorded AG-UI stream validation (SPEC-03b AC2)."""

from __future__ import annotations

from pathlib import Path

import pytest
from fixture_catalog import REPO_ROOT, load_stream_cases
from stream_harness import validate_stream_file


@pytest.mark.t("T-33")
@pytest.mark.parametrize("case", load_stream_cases(), ids=lambda case: case.file)
def test_recorded_streams_validate_both_runtimes(case) -> None:
    path = REPO_ROOT / "docs/contracts/examples" / case.file
    seq_ok, pydantic_ok, ajv_ok = validate_stream_file(path)
    if case.expect_valid:
        assert seq_ok
        assert pydantic_ok
        assert ajv_ok
        return
    assert case.expected_code in {"SEQ", "SCHEMA"}
    if case.expected_code == "SEQ":
        assert not seq_ok
        assert pydantic_ok
        assert ajv_ok
        return
    assert seq_ok
    assert not pydantic_ok
    assert not ajv_ok


@pytest.mark.t("T-33")
def test_stream_harness_does_not_write_into_repo(tmp_path: Path) -> None:
    source = REPO_ROOT / "docs/contracts/examples/agui/diagnostic-run.stream.jsonl"
    target = tmp_path / "copy.stream.jsonl"
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    before = target.read_bytes()
    validate_stream_file(target)
    assert target.read_bytes() == before
