"""T-31 checks for AC2 and AC5: make check names a failing step, and targets owned by
later specs fail with a message naming that spec."""

import subprocess
from pathlib import Path

import pytest

LATER = {
    "contracts": "SPEC-03a",
    "r0-sample": "SPEC-25",
    "release": "SPEC-01b",
    "deploy": "SPEC-01b",
    "promote": "SPEC-01b",
}


def make(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["make", "--no-print-directory", *args], cwd=root, capture_output=True, text=True
    )


@pytest.mark.t("T-31")
@pytest.mark.parametrize(("target", "spec"), sorted(LATER.items()))
def test_later_spec_target_fails_and_names_its_spec(root: Path, target: str, spec: str) -> None:
    result = make(root, target)
    assert result.returncode != 0
    assert spec in result.stdout


@pytest.mark.t("T-31")
def test_check_fails_and_names_the_failing_step(root: Path) -> None:
    result = make(root, "check", "CHECK_STEPS=selftest-pass selftest-fail selftest-pass")
    assert result.returncode != 0
    assert "FAILED at step(s): selftest-fail" in result.stdout
    assert result.stdout.count("==> make check:") == 3  # later steps still run


@pytest.mark.t("T-31")
def test_check_passes_when_every_step_passes(root: Path) -> None:
    result = make(root, "check", "CHECK_STEPS=selftest-pass")
    assert result.returncode == 0
    assert "all steps passed" in result.stdout


@pytest.mark.t("T-31")
def test_eval_reports_zero_suites(root: Path) -> None:
    result = make(root, "eval")
    assert result.returncode == 0
    assert "0 suites" in result.stdout
