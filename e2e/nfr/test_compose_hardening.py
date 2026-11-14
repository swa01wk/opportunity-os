"""T-31 static check for AC4 (ADR-015, ADR-022, NFR-12): every image pinned by digest or
built from pinned bases, private services publish nothing, published ports bind to 127.0.0.1."""

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

from nfr_support import interpolate

DIGEST = re.compile(r"^[^@\s]+:[^@\s]+@sha256:[0-9a-f]{64}$")
NOT_IMAGES = {"MINIO_SOURCE_REF"}
PUBLISHING = {"web", "api", "keycloak", "lgtm", "objectstore"}  # lgtm serves Grafana
PRIVATE = {"render", "worker", "postgres", "otel-collector"}


@pytest.fixture(scope="module")
def services(root: Path) -> dict[str, Any]:
    return yaml.safe_load((root / "compose.yaml").read_text())["services"]


@pytest.mark.t("T-31")
def test_every_pinned_image_carries_a_digest(image_pins: dict[str, str]) -> None:
    unpinned = [k for k, v in image_pins.items() if k not in NOT_IMAGES and not DIGEST.match(v)]
    assert not unpinned, f"not pinned by digest (run infra/pin.sh): {unpinned}"


@pytest.mark.t("T-31")
def test_every_service_image_is_pinned_or_built(
    services: dict[str, Any], image_pins: dict[str, str]
) -> None:
    for name, service in services.items():
        if "build" in service:
            continue
        image = interpolate(service["image"], image_pins)
        assert DIGEST.match(image), f"{name}: {image} is not pinned by digest"


@pytest.mark.t("T-31")
def test_dockerfiles_build_only_from_pinned_bases(root: Path, image_pins: dict[str, str]) -> None:
    for dockerfile in sorted((root / "docker").glob("*.Dockerfile")):
        stages: set[str] = set()
        for line in dockerfile.read_text().splitlines():
            match = re.match(r"FROM\s+(\S+)(?:\s+AS\s+(\S+))?", line, re.IGNORECASE)
            if not match:
                continue
            base, stage = match.groups()
            arg = re.fullmatch(r"\$\{([A-Z_]+)\}", base)
            assert base in stages or (arg and arg.group(1) in image_pins), (
                f"{dockerfile.name}: FROM {base} is neither a stage nor a pinned base"
            )
            if stage:
                stages.add(stage)


@pytest.mark.t("T-31")
def test_images_run_as_a_non_root_user(root: Path) -> None:
    for dockerfile in sorted((root / "docker").glob("*.Dockerfile")):
        final_stage = re.split(r"(?im)^FROM\s", dockerfile.read_text())[-1]
        users = re.findall(r"(?m)^USER\s+(\S+)", final_stage)
        assert users and users[-1] not in {"root", "0"}, f"{dockerfile.name} runs as root"


@pytest.mark.t("T-31")
def test_only_the_listed_services_publish_ports(services: dict[str, Any]) -> None:
    publishing = {name for name, service in services.items() if service.get("ports")}
    assert publishing == PUBLISHING
    assert not publishing & PRIVATE


@pytest.mark.t("T-31")
def test_published_ports_bind_to_localhost(services: dict[str, Any]) -> None:
    for name, service in services.items():
        for port in service.get("ports", []):
            assert str(port).startswith("127.0.0.1:"), f"{name} publishes {port} beyond localhost"


@pytest.mark.t("T-31")
def test_private_services_sit_only_on_the_internal_network(root: Path) -> None:
    compose = yaml.safe_load((root / "compose.yaml").read_text())
    assert compose["networks"]["private"]["internal"] is True
    for name in PRIVATE:
        assert compose["services"][name]["networks"] == ["private"], name


@pytest.mark.t("T-31")
def test_every_running_service_has_a_health_check(services: dict[str, Any]) -> None:
    for name, service in services.items():
        if "tools" in service.get("profiles", []):
            continue
        assert service.get("healthcheck", {}).get("test"), f"{name} has no health check"
