"""T-32: pipeline gates, Semgrep fixtures, gitleaks and licence checks (SPEC-02)."""

from __future__ import annotations

import subprocess
import sys
from email.message import Message
from pathlib import Path

import pytest
import yaml
from ci_support import (
    assert_pinned_actions,
    assert_top_level_permissions,
    pr_job_names,
    required_check_names,
    workflow_files,
)

from nfr_support import ROOT

LICENCE_FIXTURES = ROOT / "infra" / "ci" / "licences" / "tests"
SEMGREP_VALIDATE = ROOT / "infra" / "ci" / "semgrep" / "validate_rule_tests.py"
CHECK_LICENCES = ROOT / "infra" / "ci" / "check_licences.py"
VERIFY_ACTION_PINS = ROOT / "infra" / "ci" / "verify_action_pins.py"
GITLEAKS_VERIFY = ROOT / "infra" / "ci" / "gitleaks" / "verify_fixture.py"
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


def _message_from_fixture(raw: dict[str, object]) -> Message:
    msg = Message()
    for key, value in raw.items():
        if isinstance(value, list):
            for item in value:
                msg[key] = str(item)
        else:
            msg[key] = str(value)
    return msg


@pytest.mark.t("T-32")
@pytest.mark.parametrize(
    "fixture_path",
    [
        LICENCE_FIXTURES / "metadata-expression.yaml",
        LICENCE_FIXTURES / "metadata-classifier.yaml",
        LICENCE_FIXTURES / "metadata-long-text.yaml",
    ],
    ids=["expression", "classifier-only", "long-text"],
)
def test_licence_metadata_resolution(fixture_path: Path) -> None:
    import importlib.util

    spec = importlib.util.spec_from_file_location("check_licences", CHECK_LICENCES)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    payload = yaml.safe_load(fixture_path.read_text())
    allowlist = ROOT / "infra" / "ci" / "licences.yaml"
    _, overrides = module._load_allowlist(allowlist)
    meta = _message_from_fixture(payload["metadata"])
    assert module.resolve_license_from_metadata(meta, overrides) == payload["expected"]


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
def test_action_pins_use_annotated_sha_format() -> None:
    result = subprocess.run(
        [sys.executable, str(VERIFY_ACTION_PINS), "--format-only"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.t("T-32")
@pytest.mark.functional
def test_gitleaks_fixture_dir_scan_redacts_secret() -> None:
    result = subprocess.run(
        [sys.executable, str(GITLEAKS_VERIFY)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
