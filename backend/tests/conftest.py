"""Unit-test defaults (SPEC-08: exporters off in py-tools)."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _otel_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OTEL_SDK_DISABLED", "true")
    from opportunityos.telemetry import configure_logging

    configure_logging()
