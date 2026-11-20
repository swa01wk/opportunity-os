"""One dispatch and relay cycle for the worker loop (SPEC-09a)."""

from __future__ import annotations

import os
import threading
import time

import structlog
from sqlalchemy.engine import Engine

from opportunityos.workflows.dispatcher import dispatch_batch
from opportunityos.workflows.relay import relay_batch

_log = structlog.get_logger(__name__)


def worker_poll_cycle(engine: Engine) -> None:
    dispatch_batch(engine)
    relay_batch(engine)


def _poll_loop(engine: Engine, stop: threading.Event, interval_ms: int) -> None:
    interval_sec = max(interval_ms, 1) / 1000.0
    while not stop.is_set():
        try:
            worker_poll_cycle(engine)
        except Exception:
            _log.exception("worker.poll_failed")
        if stop.wait(interval_sec):
            return


def start_worker_poll(engine: Engine) -> tuple[threading.Event, threading.Thread]:
    stop = threading.Event()
    interval_ms = int(os.environ.get("WORKER_POLL_INTERVAL_MS", "500"))
    thread = threading.Thread(
        target=_poll_loop,
        args=(engine, stop, interval_ms),
        name="worker-poll",
        daemon=True,
    )
    thread.start()
    return stop, thread


def join_worker_poll(stop: threading.Event, thread: threading.Thread, *, deadline: float) -> None:
    stop.set()
    remaining = deadline - time.monotonic()
    if remaining > 0:
        thread.join(timeout=remaining)
