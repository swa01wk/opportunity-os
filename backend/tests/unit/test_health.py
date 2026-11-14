"""T-31: every runner is exercised; health endpoints behave as OBSERVABILITY.md says."""

import socket

import pytest
from fastapi.testclient import TestClient

from opportunityos.health import health_app, tcp_check


def ok() -> None:
    return None


def unreachable() -> None:
    raise ConnectionRefusedError


@pytest.mark.t("T-31")
def test_healthz_reports_service_and_version(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_VERSION", "abc1234")
    client = TestClient(health_app("api", {"postgres": unreachable}))
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "api", "version": "abc1234"}


@pytest.mark.t("T-31")
def test_readyz_is_ok_when_every_dependency_answers() -> None:
    client = TestClient(health_app("worker", {"postgres": ok, "objectstore": ok}))
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json()["checks"] == {"postgres": "ok", "objectstore": "ok"}


@pytest.mark.t("T-31")
def test_readyz_is_503_and_names_the_failed_dependency() -> None:
    client = TestClient(health_app("worker", {"postgres": ok, "objectstore": unreachable}))
    response = client.get("/readyz")
    assert response.status_code == 503
    assert response.json()["status"] == "unavailable"
    assert response.json()["checks"] == {"postgres": "ok", "objectstore": "fail"}


@pytest.mark.t("T-31")
def test_tcp_check_connects_to_a_listening_port() -> None:
    with socket.create_server(("127.0.0.1", 0)) as server:
        port = server.getsockname()[1]
        tcp_check(f"postgresql://u@127.0.0.1:{port}/db")()
    with pytest.raises(OSError):
        tcp_check(f"http://127.0.0.1:{port}")()
