"""Worker entry point: `python -m opportunityos.worker` (ADR-003, SPEC-09a)."""

from __future__ import annotations

import os
import threading
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from dbos import DBOS
from fastapi import FastAPI

from opportunityos.health import tcp_check
from opportunityos.telemetry import configure_logging, instrument_fastapi
from opportunityos.telemetry.log import uvicorn_log_config
from opportunityos.workflows.dbos_runtime import init_dbos, launch_dbos
from opportunityos.workflows.metrics import register_worker_metrics
from opportunityos.workflows.poll import join_worker_poll, start_worker_poll
from opportunityos.workflows.worker_db import dispose_worker_engine, worker_engine

_POLL_STOP: threading.Event | None = None
_POLL_THREAD: threading.Thread | None = None


def _bootstrap_dbos() -> None:
    init_dbos(name="worker")
    from opportunityos.workflows import noop

    noop.register_test_workflows()
    register_worker_metrics()
    launch_dbos()


@asynccontextmanager
async def _lifespan(_app: FastAPI) -> AsyncIterator[None]:
    global _POLL_STOP, _POLL_THREAD
    _bootstrap_dbos()
    engine = worker_engine()
    _POLL_STOP, _POLL_THREAD = start_worker_poll(engine)
    yield
    if _POLL_STOP is not None and _POLL_THREAD is not None:
        join_worker_poll(_POLL_STOP, _POLL_THREAD, deadline=time.monotonic() + 5.0)
    DBOS.destroy(destroy_registry=True)
    dispose_worker_engine()


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
