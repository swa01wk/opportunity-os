"""Write-path and domain errors (R-53 error classes)."""

from __future__ import annotations


class WritePathError(Exception):
    """Base for write-path failures surfaced as problem responses."""

    error_class: str = "conflict"
    http_status: int = 409

    def __init__(self, *, problem_type: str, detail: str) -> None:
        self.problem_type = problem_type
        self.detail = detail
        super().__init__(detail)


class IdempotencyKeyReused(WritePathError):
    """Same Idempotency-Key with a different request body (ADR-004, SPEC-09a AC2)."""

    error_class = "conflict"

    def __init__(self) -> None:
        super().__init__(
            problem_type="idempotency_key_reused",
            detail="This Idempotency-Key was already used with a different request body.",
        )
