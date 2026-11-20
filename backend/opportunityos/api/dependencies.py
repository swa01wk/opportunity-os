"""FastAPI dependencies for write-path headers (SPEC-09a)."""

from __future__ import annotations

from typing import Annotated

from fastapi import Header, HTTPException


def require_idempotency_key(
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> str:
    if not idempotency_key or not idempotency_key.strip():
        raise HTTPException(
            status_code=400,
            detail="Idempotency-Key header is required for this command.",
        )
    return idempotency_key.strip()


def require_if_match(
    if_match: Annotated[str | None, Header(alias="If-Match")] = None,
) -> str:
    if not if_match or not if_match.strip():
        raise HTTPException(
            status_code=400,
            detail="If-Match header is required for this update.",
        )
    return if_match.strip().strip('"')
