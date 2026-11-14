"""T-33: make contracts-check fails on drift and names the path (SPEC-03a AC2)."""

import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
COMMON_SCHEMA = REPO_ROOT / "docs/contracts/common.schema.json"


def make(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["make", "--no-print-directory", *args], cwd=root, capture_output=True, text=True
    )


@pytest.mark.t("T-33")
def test_contracts_check_fails_and_names_drifted_file(root: Path) -> None:
    if shutil.which("git") is None:
        pytest.skip("git is not available in this environment")
    original = COMMON_SCHEMA.read_text(encoding="utf-8")
    try:
        result = make(root, "contracts")
        assert result.returncode == 0, result.stderr + result.stdout
        COMMON_SCHEMA.write_text(original.replace("0.1.0", "9.9.9"), encoding="utf-8")
        drift = make(root, "contracts-check")
        assert drift.returncode != 0
        combined = drift.stdout + drift.stderr
        assert "common.schema.json" in combined
    finally:
        COMMON_SCHEMA.write_text(original, encoding="utf-8")
        make(root, "contracts")
