"""T-33: make _contracts-drift fails on drift and names the path (SPEC-03a AC2)."""

import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def make(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["make", "--no-print-directory", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


@pytest.mark.t("T-33")
def test_contracts_drift_fails_and_names_drifted_file(tmp_path: Path) -> None:
    if shutil.which("git") is None:
        pytest.fail("git is required for the contracts drift test (SPEC-03a B10)")

    shutil.copy(REPO_ROOT / "Makefile", tmp_path / "Makefile")
    shutil.copytree(REPO_ROOT / "infra", tmp_path / "infra")

    schema_dir = tmp_path / "docs" / "contracts"
    schema_dir.mkdir(parents=True)
    schema_file = schema_dir / "x.schema.json"
    schema_file.write_text('{"x-version": "0.0.0"}\n', encoding="utf-8")

    init = subprocess.run(["git", "init", "-q"], cwd=tmp_path, capture_output=True, text=True)
    assert init.returncode == 0, init.stderr
    subprocess.run(
        ["git", "config", "user.email", "contracts-test@example.invalid"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "contracts test"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "add", "docs/contracts/x.schema.json"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "baseline schema"], cwd=tmp_path, check=True)

    schema_file.write_text('{"x-version": "9.9.9"}\n', encoding="utf-8")

    drift = make(tmp_path, "_contracts-drift")
    assert drift.returncode != 0
    combined = drift.stdout + drift.stderr
    assert "x.schema.json" in combined
