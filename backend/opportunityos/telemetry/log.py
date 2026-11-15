"""structlog JSON logs with trace correlation (SPEC-08)."""

from __future__ import annotations

import logging
import sys
from typing import Any
from uuid import uuid4

import structlog
from opentelemetry import trace
from structlog.types import EventDict, Processor

from opportunityos.telemetry.redaction import redact_event_dict


def _redaction_processor(_logger: logging.Logger, _method: str, event_dict: EventDict) -> EventDict:
    return redact_event_dict(dict(event_dict))


def _add_trace_context(_logger: logging.Logger, _method: str, event_dict: EventDict) -> EventDict:
    span = trace.get_current_span()
    ctx = span.get_span_context()
    if ctx.is_valid:
        event_dict["trace_id"] = format(ctx.trace_id, "032x")
        event_dict["span_id"] = format(ctx.span_id, "016x")
    rid = structlog.contextvars.get_contextvars().get("request_id")
    if rid:
        event_dict.setdefault("request_id", rid)
    return event_dict


_SHARED_LOG_PROCESSORS: list[Processor] = [
    structlog.processors.add_log_level,
    structlog.processors.TimeStamper(fmt="iso", utc=True),
    _redaction_processor,
]


def bind_request_id(request_id: str | None = None) -> str:
    rid = request_id or uuid4().hex
    structlog.contextvars.bind_contextvars(request_id=rid)
    return rid


def configure_logging() -> None:
    level = logging.INFO
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=level)
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        *_SHARED_LOG_PROCESSORS,
        _add_trace_context,
        structlog.processors.JSONRenderer(),
    ]
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(*, component: str) -> Any:
    return structlog.get_logger(component=component)


def uvicorn_log_config() -> dict[str, Any]:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "plain": {
                "()": "structlog.stdlib.ProcessorFormatter",
                "processor": structlog.processors.JSONRenderer(),
                "foreign_pre_chain": [*_SHARED_LOG_PROCESSORS, _add_trace_context],
            }
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": "plain",
                "stream": "ext://sys.stdout",
            }
        },
        "loggers": {
            name: {"handlers": ["default"], "level": "INFO", "propagate": False}
            for name in ("uvicorn", "uvicorn.error", "uvicorn.access")
        },
    }
