"""T-32: pipeline gates, Semgrep fixtures, gitleaks and licence checks (SPEC-02)."""

from __future__ import annotations

import subprocess
import sys

import pytest
from ci_support import (
    assert_pinned_actions,
    assert_top_level_permissions,
    pr_job_names,
    required_check_names,
    workflow_files,
)

from nfr_support import ROOT

SEMGREP_VALIDATE = ROOT / "infra" / "ci" / "semgrep" / "validate_rule_tests.py"
CHECK_LICENCES = ROOT / "infra" / "ci" / "check_licences.py"
GITLEAKS_FIXTURE = ROOT / "infra" / "ci" / "gitleaks" / "tests" / "synthetic-leak.txt"
PR_YML = ROOT / ".github" / "workflows" / "pr.yml"


@pytest.mark.t("T-32")
def test_pr_job_names_match_required_checks() -> None:
    expected = required_check_names()
    assert len(expected) == 13, f"expected 13 required checks, got {expected!r}"
    assert pr_job_names(PR_YML) == sorted(expected)


@pytest.mark.t("T-32")
def test_workflows_use_pinned_actions_and_read_permissions() -> None:
    problems: list[str] = []
    for path in workflow_files():
        problems.extend(assert_pinned_actions(path))
        problems.extend(assert_top_level_permissions(path))
    assert not problems, "\n".join(problems)


@pytest.mark.t("T-32")
def test_semgrep_fixtures_cover_rules() -> None:
    result = subprocess.run(
        [sys.executable, str(SEMGREP_VALIDATE)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.t("T-32")
def test_licence_check_fixture_fails_for_disallowed() -> None:
    result = subprocess.run(
        [sys.executable, str(CHECK_LICENCES), "--fixture-only"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "oos-ci-fixture-unlicensed" in result.stderr
    assert "Proprietary-Closed" in result.stderr


@pytest.mark.t("T-32")
def test_gitleaks_fixture_and_redaction_configured() -> None:
    assert GITLEAKS_FIXTURE.is_file()
    makefile = (ROOT / "Makefile").read_text()
    assert "--redact" in makefile
    assert "synthetic-leak.txt" in makefile
