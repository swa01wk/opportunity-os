"""Alembic environment (ADR-006). `make migrate` runs `upgrade head`; SPEC-04 adds revisions."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from alembic import context
from sqlalchemy import create_engine, pool, text

_MIGRATIONS_DIR = Path(__file__).resolve().parent
if str(_MIGRATIONS_DIR) not in sys.path:
    sys.path.insert(0, str(_MIGRATIONS_DIR))

url = os.environ["MIGRATE_DATABASE_URL"]

if context.is_offline_mode():
    context.configure(url=url, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    engine = create_engine(url, poolclass=pool.NullPool)
    with engine.begin() as connection:
        connection.execute(text("SET lock_timeout = '30s'"))
        context.configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()
