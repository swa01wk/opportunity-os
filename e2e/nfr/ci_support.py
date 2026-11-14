"""Helpers for SPEC-02 pipeline static checks (T-32)."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"
TEST_STRATEGY = ROOT / "plans" / "TEST_STRATEGY.md"

REQUIRED_CHECKS_LINE = "**Required checks** on `main` (added to the ruleset when SPEC-02 merges): "

PINNED_USES = re.compile(
    r"^\s+-?\s*uses:\s*(?P<action>[\w./-]+)@(?P<sha>[a-f0-9]{40})\s+#\s*v(?P<tag>[\d.]+)\s*$"
)


def required_check_names() -> list[str]:
    text = TEST_STRATEGY.read_text()
    start = text.index(REQUIRED_CHECKS_LINE)
    line = text[start : text.find("\n", start)]
    backtick_parts = re.findall(r"`([^`]+)`", line)
    return backtick_parts[1:]


def pr_job_names(pr_yml: Path) -> list[str]:
    doc = yaml.safe_load(pr_yml.read_text())
    jobs = doc.get("jobs") or {}
    return sorted(jobs.keys())


def workflow_files() -> list[Path]:
    return sorted(WORKFLOWS.glob("*.yml"))


def assert_pinned_actions(path: Path) -> list[str]:
    issues: list[str] = []
    for lineno, line in enumerate(path.read_text().splitlines(), start=1):
        if "uses:" not in line or "${{" in line:
            continue
        if "actions/" not in line:
            continue
        if PINNED_USES.match(line):
            continue
        issues.append(
            f"{path.name}:{lineno}: must be action@40-hex-sha # vX.Y.Z — got {line.strip()}"
        )
    return issues


def assert_top_level_permissions(path: Path) -> list[str]:
    doc = yaml.safe_load(path.read_text())
    perms = doc.get("permissions")
    if perms is None:
        return [f"{path.name}: missing top-level permissions"]
    if perms.get("contents") != "read":
        return [f"{path.name}: permissions.contents must be read"]
    return []
