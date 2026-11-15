"""OpenTelemetry SDK bootstrap for api and worker (SPEC-08)."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

if TYPE_CHECKING:
    from fastapi import FastAPI

_CONFIGURED = False


def _sdk_disabled() -> bool:
    return os.environ.get("OTEL_SDK_DISABLED", "").lower() in ("true", "1", "yes")


def _resource(service_name: str) -> Resource:
    attrs = {
        "service.name": service_name,
        "service.version": os.environ.get("APP_VERSION", "unknown"),
        "deployment.environment": os.environ.get("APP_ENV", "dev"),
    }
    return Resource.create(attrs)


def configure_otel(service_name: str) -> None:
    global _CONFIGURED
    if _CONFIGURED or _sdk_disabled():
        return
    resource = _resource(service_name)
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4318")

    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces"))
    )
    trace.set_tracer_provider(tracer_provider)

    reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=f"{endpoint}/v1/metrics"))
    metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[reader]))

    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(OTLPLogExporter(endpoint=f"{endpoint}/v1/logs"))
    )
    handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
    logging.getLogger().addHandler(handler)

    _CONFIGURED = True


def instrument_fastapi(app: FastAPI, *, service_name: str) -> None:
    configure_otel(service_name)
    if _sdk_disabled():
        return
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    FastAPIInstrumentor.instrument_app(app, excluded_urls="healthz,readyz")
