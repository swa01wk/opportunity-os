"""Logger-side redaction (OBSERVABILITY.md); mirrored again in the Collector."""

from __future__ import annotations

import re
from typing import Any

# Keys dropped entirely (case-insensitive match on the leaf key).
DROP_KEY = re.compile(
    r"(?i)^(authorization|cookie|set-cookie|password|client_secret|api_key|"
    r"access_token|refresh_token|id_token|storage_secret_key|smtp_password|"
    r"keycloak_client_secret|auth_secret|openai_api_key|elevenlabs_api_key|"
    r"search_api_key|token_encryption_key)$"
)
CREDENTIAL_KEY = re.compile(
    r"(?i)(^|[._-])(access|refresh|id|session|bearer|auth|api)[._-]?(token|key)($|[._-])"
    r"|(?:secret|password|credential|api[_-]?key)"
)
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
SK_PREFIX = re.compile(r"\bsk-[A-Za-z0-9]{16,}\b")
SIGNED_URL = re.compile(
    r"(?i)([?&](X-Amz-Signature|X-Amz-Credential|X-Amz-Security-Token|"
    r"sig|signature|token)=[^&\s]+)"
)
MASK = "[redacted]"


def _redact_value(key: str, value: Any) -> Any:
    if DROP_KEY.search(key) or CREDENTIAL_KEY.search(key):
        return MASK
    if isinstance(value, str):
        if EMAIL.search(value):
            value = EMAIL.sub(MASK, value)
        if SK_PREFIX.search(value):
            value = SK_PREFIX.sub(MASK, value)
        if SIGNED_URL.search(value):
            value = SIGNED_URL.sub(lambda m: m.group(0).split("=")[0] + "=" + MASK, value)
    elif isinstance(value, dict):
        return {k: _redact_value(k, v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_redact_value(key, item) for item in value]
    return value


def redact_event_dict(event_dict: dict[str, Any], *, enabled: bool = True) -> dict[str, Any]:
    if not enabled:
        return event_dict
    out: dict[str, Any] = {}
    for key, value in event_dict.items():
        if DROP_KEY.search(key):
            continue
        out[key] = _redact_value(key, value)
    return out
