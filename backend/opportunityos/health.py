"""Liveness and readiness endpoints shared by the api and worker (OBSERVABILITY.md).

/healthz answers while the process runs. /readyz checks only the dependencies the
service has (SPEC-01a): PostgreSQL for api and worker, the object store for worker.
A dependency counts as reachable when it accepts a connection; SPEC-08 adds telemetry.
"""

import os
import socket
from collections.abc import Callable, Mapping
from urllib.parse import urlsplit

from fastapi import APIRouter, FastAPI
from fastapi.responses import JSONResponse

Check = Callable[[], None]
TIMEOUT_SECONDS = 2.0


def version() -> str:
    return os.environ.get("APP_VERSION", "unknown")


def tcp_check(url: str) -> Check:
    """Pass when a TCP connection to the URL's host and port succeeds."""
    parts = urlsplit(url)
    host = parts.hostname or "localhost"
    port = parts.port or (443 if parts.scheme == "https" else 80)

    def check() -> None:
        with socket.create_connection((host, port), timeout=TIMEOUT_SECONDS):
            pass

    return check


def health_router(service: str, checks: Mapping[str, Check]) -> APIRouter:
    router = APIRouter()

    @router.get("/healthz", include_in_schema=False)
    def healthz() -> dict[str, str]:
        return {"status": "ok", "service": service, "version": version()}

    @router.get("/readyz", include_in_schema=False)
    def readyz() -> JSONResponse:
        failed = []
        for name, check in checks.items():
            try:
                check()
            except OSError:
                failed.append(name)
        body: dict[str, object] = {
            "status": "unavailable" if failed else "ok",
            "service": service,
            "version": version(),
            "checks": {name: ("fail" if name in failed else "ok") for name in checks},
        }
        return JSONResponse(body, status_code=503 if failed else 200)

    return router


def health_app(service: str, checks: Mapping[str, Check]) -> FastAPI:
    app = FastAPI(title=f"opportunityos-{service}", docs_url=None, redoc_url=None)
    app.include_router(health_router(service, checks))
    return app
