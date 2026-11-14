# ruff: noqa: S608 — positive Semgrep fixture for string-built SQL (T-32).
from sqlalchemy import text


def bad_execute(cursor) -> None:
    table = "app.project"
    # ruleid: oos.python.string-built-sql
    cursor.execute(f"SELECT 1 FROM {table}")


# ok: oos.python.string-built-sql
def good_execute(cursor) -> None:
    cursor.execute(text("SELECT 1 FROM app.project WHERE id = :id"), {"id": "1"})
