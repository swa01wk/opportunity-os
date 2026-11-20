"""Write-path header dependencies (SPEC-09a)."""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from opportunityos.api.dependencies import require_idempotency_key, require_if_match


def test_require_idempotency_key_rejects_missing() -> None:
    with pytest.raises(HTTPException) as exc:
        require_idempotency_key(None)
    assert exc.value.status_code == 400


def test_require_if_match_rejects_missing() -> None:
    with pytest.raises(HTTPException) as exc:
        require_if_match(None)
    assert exc.value.status_code == 400


def test_require_if_match_strips_quotes() -> None:
    assert require_if_match('"3"') == "3"
