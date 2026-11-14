"""Lightweight Semgrep rule/fixture cross-check for make check (T-32).

Full ``semgrep --test`` runs on the host via ``make _host-semgrep-rules-test``.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
RULES_DIR = ROOT / "infra" / "ci" / "semgrep" / "rules"
TESTS_DIR = ROOT / "infra" / "ci" / "semgrep" / "tests"

RULEID = re.compile(r"^\s*# ruleid:\s*(\S+)", re.MULTILINE)
OKID = re.compile(r"^\s*# ok:\s*(\S+)", re.MULTILINE)
TS_RULEID = re.compile(r"^\s*// ruleid:\s*(\S+)", re.MULTILINE)
TS_OKID = re.compile(r"^\s*// ok:\s*(\S+)", re.MULTILINE)


def _rule_ids() -> set[str]:
    ids: set[str] = set()
    for path in sorted(RULES_DIR.glob("*.yaml")):
        docs = yaml.safe_load_all(path.read_text())
        for doc in docs:
            if not doc:
                continue
            for rule in doc.get("rules", []):
                rule_id = rule.get("id")
                if rule_id:
                    ids.add(str(rule_id))
    return ids


def _fixture_ids(path: Path) -> tuple[set[str], set[str]]:
    text = path.read_text()
    if path.suffix in {".ts", ".tsx"}:
        positives = set(TS_RULEID.findall(text))
        negatives = set(TS_OKID.findall(text))
    else:
        positives = set(RULEID.findall(text))
        negatives = set(OKID.findall(text))
    return positives, negatives


def validate() -> list[str]:
    errors: list[str] = []
    known = _rule_ids()
    if not known:
        errors.append("no Semgrep rules found under infra/ci/semgrep/rules")
        return errors

    positives_all: set[str] = set()
    for path in sorted(TESTS_DIR.iterdir()):
        if path.is_dir() or path.name.startswith("."):
            continue
        if path.name.startswith("fixture-"):
            continue
        positives, negatives = _fixture_ids(path)
        for rule_id in positives | negatives:
            if rule_id not in known:
                errors.append(f"{path.name}: unknown rule id {rule_id!r}")
        if not positives:
            errors.append(f"{path.name}: missing at least one ruleid: positive fixture")
        if not negatives:
            errors.append(f"{path.name}: missing at least one ok: negative fixture")
        positives_all |= positives

    for rule_id in sorted(known):
        if rule_id not in positives_all:
            errors.append(f"rule {rule_id!r} has no positive fixture in infra/ci/semgrep/tests")
    return errors


def main() -> int:
    problems = validate()
    if problems:
        for line in problems:
            print(f"T-32 Semgrep fixtures: {line}")
        return 1
    print("T-32 Semgrep fixtures: rule ids and positive/negative markers OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
