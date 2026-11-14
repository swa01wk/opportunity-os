#!/usr/bin/env python3
"""Verify workflow action SHAs match annotated tag refs (SPEC-02, T-32)."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"

PINNED_USES = re.compile(
    r"^\s+-?\s*uses:\s*(?P<action>[\w./-]+)@(?P<sha>[a-f0-9]{40})\s+#\s*v(?P<tag>[\d.]+)\s*$"
)


def workflow_action_pins() -> list[tuple[str, str, str, str]]:
    """Return (workflow, action, sha, tag) for each pinned uses line."""
    found: list[tuple[str, str, str, str]] = []
    for path in sorted(WORKFLOWS.glob("*.yml")):
        for line in path.read_text().splitlines():
            match = PINNED_USES.match(line)
            if not match:
                continue
            found.append((path.name, match.group("action"), match.group("sha"), match.group("tag")))
    return found


def assert_pin_comment_format() -> list[str]:
    errors: list[str] = []
    for path in sorted(WORKFLOWS.glob("*.yml")):
        for lineno, line in enumerate(path.read_text().splitlines(), start=1):
            if "uses:" not in line or "${{" in line:
                continue
            if "actions/" not in line:
                continue
            if PINNED_USES.match(line):
                continue
            errors.append(
                f"{path.name}:{lineno}: actions/uses must be @40-hex-sha # vX.Y.Z: {line.strip()}"
            )
    return errors


def resolve_tag_sha(action: str, tag: str) -> str | None:
    repo = f"https://github.com/{action}.git"
    ref = f"refs/tags/v{tag}"
    result = subprocess.run(
        ["git", "ls-remote", repo, ref],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    for row in result.stdout.splitlines():
        if "\t" not in row:
            continue
        sha, name = row.split("\t", 1)
        if name.strip() == ref:
            return sha.strip()
    return None


def verify_pins() -> list[str]:
    problems: list[str] = list(assert_pin_comment_format())
    for workflow, action, sha, tag in workflow_action_pins():
        resolved = resolve_tag_sha(action, tag)
        if resolved is None:
            problems.append(f"{workflow}: git ls-remote failed for {action} v{tag}")
            continue
        if resolved != sha:
            problems.append(
                f"{workflow}: {action}@{sha} does not match v{tag} (expected {resolved})"
            )
    return problems


def main() -> int:
    format_only = "--format-only" in sys.argv
    problems = assert_pin_comment_format() if format_only else verify_pins()
    if problems:
        print("action pin check:", file=sys.stderr)
        for line in problems:
            print(f"  {line}", file=sys.stderr)
        return 1
    print("action pin check: workflow SHAs match annotated tags")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
