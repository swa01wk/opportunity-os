"""Helpers for SPEC-02 pipeline static checks (T-32)."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"
TEST_STRATEGY = ROOT / "plans" / "TEST_STRATEGY.md"

REQUIRED_CHECKS_LINE = "**Required checks** on `main` (added to the ruleset when SPEC-02 merges): "

USES_LINE = re.compile(r"^\s+uses:\s*(?P<ref>.+)$", re.MULTILINE)


def required_check_names() -> list[str]:
    text = TEST_STRATEGY.read_text()
    start = text.index(REQUIRED_CHECKS_LINE)
    line = text[start : text.find("\n", start)]
    backtick_parts = re.findall(r"`([^`]+)`", line)
    # First backtick pair is `main`; the rest are required check job names.
    return backtick_parts[1:]


def pr_job_names(pr_yml: Path) -> list[str]:
    doc = yaml.safe_load(pr_yml.read_text())
    jobs = doc.get("jobs") or {}
    return sorted(jobs.keys())


def workflow_files() -> list[Path]:
    return sorted(WORKFLOWS.glob("*.yml"))


def assert_pinned_actions(path: Path) -> list[str]:
    issues: list[str] = []
    for match in USES_LINE.finditer(path.read_text()):
        ref = match.group("ref").strip()
        if "${{" in ref:
            continue
        if "@" not in ref:
            issues.append(f"{path.name}: unpinned action {ref!r}")
            continue
        _repo, version = ref.rsplit("@", 1)
        version = version.strip()
        if not (
            re.fullmatch(r"[a-f0-9]{40}", version)
            or re.fullmatch(r"[a-f0-9]{64}", version)
            or version.startswith("sha256:")
        ):
            issues.append(f"{path.name}: action not pinned by commit SHA: {ref!r}")
    return issues


def assert_top_level_permissions(path: Path) -> list[str]:
    doc = yaml.safe_load(path.read_text())
    perms = doc.get("permissions")
    if perms is None:
        return [f"{path.name}: missing top-level permissions"]
    if perms.get("contents") != "read":
        return [f"{path.name}: permissions.contents must be read"]
    return []
