"""Poll an HTTP URL until it returns the expected status (SPEC-08 functional tests)."""

from __future__ import annotations

import time

import requests


def wait_http_ready(url: str, *, status: int = 200, timeout: float = 120) -> None:
    stop = time.monotonic() + timeout
    while time.monotonic() < stop:
        try:
            resp = requests.get(url, timeout=2)
            if resp.status_code == status:
                return
        except requests.RequestException:
            pass
        time.sleep(0.25)
    msg = f"timed out waiting for {url} to return HTTP {status}"
    raise TimeoutError(msg)
