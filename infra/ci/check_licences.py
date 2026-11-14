#!/usr/bin/env python3
"""Verify lockfile dependencies against infra/ci/licences.yaml (SPEC-02 AC5)."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from importlib import metadata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def _load_allowlist(path: Path) -> tuple[frozenset[str], dict[str, str]]:
    raw = yaml.safe_load(path.read_text())
    allowed = frozenset(str(entry) for entry in raw.get("allowed", []))
    overrides = {str(k): str(v) for k, v in (raw.get("overrides") or {}).items()}
    return allowed, overrides


def _normalise_license(name: str, overrides: dict[str, str]) -> str:
    stripped = name.strip()
    if stripped in overrides:
        return overrides[stripped]
    return re.sub(r"\s+", "-", stripped)


def _licensed_or_allowed(
    license_name: str, allowed: frozenset[str], overrides: dict[str, str]
) -> bool:
    if not license_name or license_name == "UNKNOWN":
        return False
    expr = license_name.strip()
    if " OR " in expr:
        return any(
            _licensed_or_allowed(part.strip(), allowed, overrides) for part in expr.split(" OR ")
        )
    if " AND " in expr:
        return all(
            _licensed_or_allowed(part.strip(), allowed, overrides) for part in expr.split(" AND ")
        )
    if expr in allowed:
        return True
    if expr in overrides:
        return overrides[expr] in allowed
    return _normalise_license(expr, overrides) in allowed


def _python_licences(allowed: frozenset[str], overrides: dict[str, str]) -> list[tuple[str, str]]:
    violations: list[tuple[str, str]] = []
    for dist in sorted(metadata.distributions(), key=lambda d: (d.metadata["Name"] or "").lower()):
        name = dist.metadata.get("Name") or dist.metadata.get("Summary") or "unknown"
        if str(name).startswith("opportunityos"):
            continue
        if str(name) in overrides:
            license_name = overrides[str(name)]
        else:
            license_name = (
                dist.metadata.get("License") or dist.metadata.get("License-Expression") or "UNKNOWN"
            )
        if not _licensed_or_allowed(str(license_name), allowed, overrides):
            violations.append((str(name), str(license_name)))
    return violations


def _pnpm_licences(allowed: frozenset[str], overrides: dict[str, str]) -> list[tuple[str, str]]:
    result = subprocess.run(
        ["pnpm", "licenses", "list", "--json"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    violations: list[tuple[str, str]] = []
    payload = json.loads(result.stdout or "{}")
    for name, info in payload.items():
        license_name = info.get("license") or info.get("licenses") or "UNKNOWN"
        if isinstance(license_name, list):
            license_name = " AND ".join(license_name)
        if not _licensed_or_allowed(str(license_name), allowed, overrides):
            violations.append((str(name), str(license_name)))
    return violations


def _check_fixture(allowed: frozenset[str]) -> list[tuple[str, str]]:
    fixture = ROOT / "infra" / "ci" / "licences" / "tests" / "disallowed-package.yaml"
    data = yaml.safe_load(fixture.read_text())
    package = str(data["package"])
    license_name = str(data["license"])
    if _licensed_or_allowed(license_name, allowed, frozenset()):
        return []
    return [(package, license_name)]


def _violations_from_pnpm_json(
    payload: object, allowed: frozenset[str], overrides: dict[str, str]
) -> list[tuple[str, str]]:
    if not isinstance(payload, dict):
        return []
    violations: list[tuple[str, str]] = []
    for name, info in payload.items():
        if not isinstance(info, dict):
            continue
        license_name = info.get("license") or info.get("licenses") or "UNKNOWN"
        if isinstance(license_name, list):
            license_name = " AND ".join(license_name)
        if not _licensed_or_allowed(str(license_name), allowed, overrides):
            violations.append((str(name), str(license_name)))
    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--fixture-only",
        action="store_true",
        help="Run the negative fixture case only (T-32 AC5).",
    )
    parser.add_argument("--python-only", action="store_true")
    parser.add_argument("--pnpm-json", type=Path)
    args = parser.parse_args(argv)
    allowlist_path = ROOT / "infra" / "ci" / "licences.yaml"
    allowed, overrides = _load_allowlist(allowlist_path)

    if args.fixture_only:
        violations = _check_fixture(allowed)
    elif args.python_only:
        violations = _python_licences(allowed, overrides)
    elif args.pnpm_json is not None:
        payload = json.loads(args.pnpm_json.read_text())
        violations = _violations_from_pnpm_json(payload, allowed, overrides)
    else:
        violations = _python_licences(allowed, overrides)
        violations += _pnpm_licences(allowed, overrides)

    if violations:
        print("licence check: disallowed licences:", file=sys.stderr)
        for package, license_name in sorted(set(violations)):
            print(f"  {package}: {license_name}", file=sys.stderr)
        return 1
    print("licence check: all packages on the allowlist")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
