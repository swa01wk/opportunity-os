"""Shared SQLAlchemy engine for the worker (SPEC-09a)."""

from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

_ENGINE: Engine | None = None


def worker_engine() -> Engine:
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = create_engine(os.environ["DATABASE_URL"])
    return _ENGINE


def dispose_worker_engine() -> None:
    global _ENGINE
    if _ENGINE is not None:
        _ENGINE.dispose()
        _ENGINE = None
