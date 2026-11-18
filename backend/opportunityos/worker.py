"""Worker entry point: `python -m opportunityos.worker` (ADR-003, SPEC-09a)."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from opportunityos.health import tcp_check
from opportunityos.telemetry import configure_logging, instrument_fastapi
from opportunityos.telemetry.log import uvicorn_log_config
from opportunityos.workflows.dbos_runtime import init_dbos, launch_dbos
from opportunityos.workflows.metrics import register_worker_metrics


def _bootstrap_dbos() -> None:
    init_dbos(name="worker")
    from opportunityos.workflows import noop

    noop.register_test_workflows()
    register_worker_metrics()
    launch_dbos()


@asynccontextmanager
async def _lifespan(_app: FastAPI) -> AsyncIterator[None]:
    _bootstrap_dbos()
    yield


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="opportunityos-worker", docs_url=None, redoc_url=None, lifespan=_lifespan)
    from opportunityos.health import health_router

    app.include_router(
        health_router(
            "worker",
            {
                "postgres": tcp_check(os.environ["DATABASE_URL"]),
                "objectstore": tcp_check(os.environ["OBJECTSTORE_ENDPOINT"]),
            },
        ),
    )
    instrument_fastapi(app, service_name="worker")
    return app


if __name__ == "__main__":
    uvicorn.run(
        create_app(),
        host="0.0.0.0",  # noqa: S104 - private network only, no host port (SPEC-01a)
        port=int(os.environ.get("PORT", "8001")),
        log_config=uvicorn_log_config(),
    )
