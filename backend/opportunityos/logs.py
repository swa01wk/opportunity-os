"""JSON log lines on stdout until SPEC-08 wires structlog and OpenTelemetry (ADR-016)."""

import json
import logging
from datetime import UTC, datetime
from typing import Any


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        line = {
            "ts": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname.lower(),
            "logger": record.name,
            "event": record.getMessage(),
        }
        return json.dumps(line)


def uvicorn_log_config() -> dict[str, Any]:
    handler = {"class": "logging.StreamHandler", "formatter": "json", "stream": "ext://sys.stdout"}
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"json": {"()": JsonFormatter}},
        "handlers": {"stdout": handler},
        "loggers": {
            name: {"handlers": ["stdout"], "level": "INFO", "propagate": False}
            for name in ("uvicorn", "uvicorn.error", "uvicorn.access")
        },
    }
