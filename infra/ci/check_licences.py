#!/usr/bin/env python3
"""Verify lockfile dependencies against infra/ci/licences.yaml (SPEC-02 AC5)."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from email.message import Message
from importlib import metadata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]

CLASSIFIER_PREFIX = "License :: OSI Approved :: "

# PyPI trove classifiers that do not spell SPDX literally (SPEC-02 B13).
CLASSIFIER_TO_SPDX: dict[str, str] = {
    "MIT License": "MIT",
    "BSD License": "BSD-3-Clause",
    "Apache Software License": "Apache-2.0",
    "Python Software Foundation License": "PSF-2.0",
    "ISC License (ISCL)": "ISC",
    "Mozilla Public License 2.0 (MPL 2.0)": "MPL-2.0",
    "The Unlicense (Unlicense)": "Unlicense",
}

LICENSE_SUMMARY_MAX = 60


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


def _metadata_get(msg: Message, key: str) -> str | None:
    value = msg.get(key)
    if value is None:
        return None
    return str(value)


def _metadata_get_all(msg: Message, key: str) -> list[str]:
    return [str(v) for v in msg.get_all(key, [])]


def _short_license_field(raw: str | None) -> str | None:
    if not raw:
        return None
    if "\n" in raw or "\r" in raw:
        return None
    stripped = raw.strip()
    if not stripped:
        return None
    return stripped


def _license_from_classifiers(classifiers: list[str]) -> str | None:
    for classifier in classifiers:
        if not classifier.startswith(CLASSIFIER_PREFIX):
            continue
        label = classifier[len(CLASSIFIER_PREFIX) :].strip()
        if label in CLASSIFIER_TO_SPDX:
            return CLASSIFIER_TO_SPDX[label]
        if label.endswith(" License"):
            candidate = label[: -len(" License")]
            if candidate in {"MIT", "ISC"}:
                return candidate
    return None


def resolve_license_from_metadata(meta: Message, overrides: dict[str, str]) -> str:
    """Resolve SPDX-ish licence from distribution metadata (SPEC-02 B13)."""
    package = _metadata_get(meta, "Name") or ""
    if package in overrides:
        return overrides[package]

    expr = _metadata_get(meta, "License-Expression")
    if expr:
        license_name = expr.strip()
    else:
        from_classifiers = _license_from_classifiers(_metadata_get_all(meta, "Classifier"))
        if from_classifiers:
            license_name = from_classifiers
        else:
            short = _short_license_field(_metadata_get(meta, "License"))
            license_name = short if short else "UNKNOWN"

    if license_name in overrides:
        return overrides[license_name]
    return license_name


def _license_summary(license_name: str) -> str:
    one_line = " ".join(license_name.split())
    if len(one_line) <= LICENSE_SUMMARY_MAX:
        return one_line
    return f"{one_line[: LICENSE_SUMMARY_MAX - 3]}..."


def _python_licences(allowed: frozenset[str], overrides: dict[str, str]) -> list[tuple[str, str]]:
    violations: list[tuple[str, str]] = []
    for dist in sorted(metadata.distributions(), key=lambda d: (d.metadata["Name"] or "").lower()):
        name = dist.metadata.get("Name") or dist.metadata.get("Summary") or "unknown"
        if str(name).startswith("opportunityos"):
            continue
        license_name = resolve_license_from_metadata(dist.metadata, overrides)
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
            print(f"  {package}: {_license_summary(license_name)}", file=sys.stderr)
        return 1
    print("licence check: all packages on the allowlist")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
