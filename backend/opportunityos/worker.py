"""Worker entry point: `python -m opportunityos.worker`.

DBOS workflows arrive in SPEC-09a/09b (ADR-003). Until then the worker only serves
its health endpoints on a private port so Compose can check it.
"""

import os

import uvicorn
from fastapi import FastAPI

from opportunityos.health import health_app, tcp_check
from opportunityos.telemetry import configure_logging, instrument_fastapi
from opportunityos.telemetry.log import uvicorn_log_config


def create_app() -> FastAPI:
    configure_logging()
    app = health_app(
        "worker",
        {
            "postgres": tcp_check(os.environ["DATABASE_URL"]),
            "objectstore": tcp_check(os.environ["OBJECTSTORE_ENDPOINT"]),
        },
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
