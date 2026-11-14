#!/usr/bin/env python3
"""T-32 AC2: gitleaks dir scan names file and rule without echoing the secret value."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import docker

ROOT = Path(__file__).resolve().parents[3]
IMAGES_ENV = ROOT / "infra" / "images.env"
FIXTURE_FILE = ROOT / "infra" / "ci" / "gitleaks" / "tests" / "synthetic-leak.txt"

GITLEAKS_IMAGE = re.compile(r"^GITLEAKS_IMAGE=(.+)$", re.MULTILINE)
SECRET_VALUE = re.compile(r"OOS_T32_FIXTURE_SECRET=([0-9a-f]{48})")


def _host_repo_mount() -> tuple[str, str]:
    """Return (host_path, container_path) for the repo bind mount (nested Docker on macOS)."""
    host = os.environ.get("OOS_HOST_REPO")
    if host:
        return host, "/repo"
    for line in Path("/proc/mounts").read_text().splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "/repo":
            return parts[0], "/repo"
    return str(ROOT), "/repo"


def _gitleaks_image() -> str:
    text = IMAGES_ENV.read_text()
    match = GITLEAKS_IMAGE.search(text)
    if not match:
        msg = "GITLEAKS_IMAGE not found in infra/images.env"
        raise RuntimeError(msg)
    return match.group(1).strip()


def _fixture_secret() -> str:
    text = FIXTURE_FILE.read_text()
    match = SECRET_VALUE.search(text)
    if not match:
        msg = "fixture secret pattern missing from synthetic-leak.txt"
        raise RuntimeError(msg)
    return match.group(1)


def verify_dir_scan(*, image: str | None = None) -> list[str]:
    image = image or _gitleaks_image()
    secret = _fixture_secret()
    host_path, container_path = _host_repo_mount()
    client = docker.from_env()
    command = [
        "dir",
        "-v",
        "--redact=100",
        "--no-banner",
        "-c",
        f"{container_path}/infra/ci/gitleaks/fixture-scan.toml",
        f"{container_path}/infra/ci/gitleaks/tests/synthetic-leak.txt",
    ]
    volumes = {host_path: {"bind": container_path, "mode": "ro"}}
    container = client.containers.create(
        image,
        command=command,
        volumes=volumes,
        working_dir=container_path,
    )
    try:
        container.start()
        result = container.wait()
        exit_status = int(result.get("StatusCode", 0))
        combined = container.logs(stdout=True, stderr=True).decode("utf-8", errors="replace")
    finally:
        container.remove(force=True)

    problems: list[str] = []
    if exit_status == 0:
        problems.append("gitleaks dir: expected exit 1 when the fixture leaks, got 0")
    if "synthetic-leak.txt" not in combined:
        problems.append("gitleaks dir: output must name synthetic-leak.txt")
    if "generic-api-key" not in combined:
        problems.append("gitleaks dir: output must name rule id generic-api-key")
    if secret in combined:
        problems.append("gitleaks dir: secret value must not appear in output (redact)")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-docker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.skip_docker:
        return 0
    problems = verify_dir_scan()
    if problems:
        for line in problems:
            print(f"T-32 gitleaks: {line}", file=sys.stderr)
        return 1
    print("T-32 gitleaks: fixture dir scan redacts the secret value")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
