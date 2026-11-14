"""API entry point: `python -m opportunityos.api.main` (ADR-004). Routers arrive in later specs."""

import os

import uvicorn
from fastapi import FastAPI

from opportunityos.health import health_app, tcp_check
from opportunityos.logs import uvicorn_log_config


def create_app() -> FastAPI:
    return health_app("api", {"postgres": tcp_check(os.environ["DATABASE_URL"])})


if __name__ == "__main__":
    uvicorn.run(
        create_app(),
        host="0.0.0.0",  # noqa: S104 - container port; Compose binds the host side to 127.0.0.1
        port=int(os.environ.get("PORT", "8000")),
        log_config=uvicorn_log_config(),
    )
