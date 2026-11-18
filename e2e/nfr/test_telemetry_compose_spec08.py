"""T-38 static checks for SPEC-08 Grafana wiring and PostgreSQL slow-query threshold."""

import json
from pathlib import Path

import pytest
import yaml


@pytest.mark.t("T-38")
def test_postgres_slow_query_threshold_in_compose(root: Path) -> None:
    services = yaml.safe_load((root / "compose.yaml").read_text())["services"]
    command = services["postgres"]["command"]
    assert "log_min_duration_statement=500" in command


@pytest.mark.t("T-38")
def test_lgtm_retention_env_in_compose(root: Path) -> None:
    env = yaml.safe_load((root / "compose.yaml").read_text())["services"]["lgtm"]["environment"]
    assert "90d" in env["PROMETHEUS_EXTRA_ARGS"]
    assert "compactor.retention-enabled=true" in env["LOKI_EXTRA_ARGS"]


@pytest.mark.t("T-38")
def test_stack_health_dashboard_uses_service_up_gauge(root: Path) -> None:
    dashboard = json.loads((root / "infra/grafana/dashboards/stack-health.json").read_text())
    targets = [
        target["expr"]
        for panel in dashboard["panels"]
        for target in panel.get("targets", [])
        if "expr" in target
    ]
    assert any("oos_service_up" in expr or "oos.service.up" in expr for expr in targets)
    assert any("http_server_request_duration_seconds" in expr for expr in targets)
