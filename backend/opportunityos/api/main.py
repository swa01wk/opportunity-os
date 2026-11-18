"""API entry point: `python -m opportunityos.api.main` (ADR-004). Routers arrive in later specs."""

import os

import uvicorn
from fastapi import FastAPI

from opportunityos.health import health_app, tcp_check
from opportunityos.telemetry import configure_logging, instrument_fastapi
from opportunityos.telemetry.log import uvicorn_log_config


def create_app() -> FastAPI:
    configure_logging()
    app = health_app("api", {"postgres": tcp_check(os.environ["DATABASE_URL"])})
    instrument_fastapi(app, service_name="api")
    return app


if __name__ == "__main__":
    uvicorn.run(
        create_app(),
        host="0.0.0.0",  # noqa: S104 - container port; Compose binds the host side to 127.0.0.1
        port=int(os.environ.get("PORT", "8000")),
        log_config=uvicorn_log_config(),
    )
