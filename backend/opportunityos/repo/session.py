"""Workspace-scoped database sessions (NFR-04, SPEC-04)."""

from __future__ import annotations

import re
from collections.abc import Iterator
from contextlib import contextmanager
from uuid import UUID

from sqlalchemy import Engine, text
from sqlalchemy.engine import Connection

_ALLOWED_ROLES = frozenset(
    {
        "oos_api",
        "oos_worker",
        "oos_render",
        "oos_retention",
        "oos_analytics_ro",
    }
)


def _pg_ident(name: str) -> str:
    if not re.fullmatch(r"[a-z_][a-z0-9_]*", name):
        msg = f"invalid SQL role name: {name!r}"
        raise ValueError(msg)
    return name


@contextmanager
def workspace_transaction(
    bind: Engine | Connection,
    *,
    role: str,
    workspace_id: UUID | None,
) -> Iterator[Connection]:
    """Open a transaction with the service role and optional workspace scope."""
    if role not in _ALLOWED_ROLES:
        msg = f"unsupported database role: {role!r}"
        raise ValueError(msg)

    own_connection = False
    if isinstance(bind, Engine):
        connection = bind.connect()
        own_connection = True
    else:
        connection = bind

    trans = connection.begin()
    try:
        connection.execute(text(f"SET LOCAL ROLE {_pg_ident(role)}"))
        if workspace_id is not None:
            connection.execute(
                text("SELECT set_config('app.workspace_id', :wid, true)"),
                {"wid": str(workspace_id)},
            )
        yield connection
        trans.commit()
    except Exception:
        trans.rollback()
        raise
    finally:
        if own_connection:
            connection.close()
