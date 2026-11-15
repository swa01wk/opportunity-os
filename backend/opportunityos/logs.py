"""Re-export logging config (SPEC-08: structlog and OpenTelemetry)."""

from opportunityos.telemetry.log import uvicorn_log_config

__all__ = ["uvicorn_log_config"]
