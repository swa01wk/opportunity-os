"""T-38: structlog redaction processor (SPEC-08)."""

import pytest

from opportunityos.telemetry.redaction import redact_event_dict


@pytest.mark.t("T-38")
def test_redaction_masks_email_and_signed_urls() -> None:
    raw = {
        "event": "export.built",
        "contact": "owner@example.com",
        "url": "https://objects.local/file?X-Amz-Signature=deadbeef&part=1",
        "safe_id": "proj-00000000-0000-4000-8000-000000000001",
    }
    redacted = redact_event_dict(raw)
    assert "owner@example.com" not in str(redacted)
    assert "deadbeef" not in redacted["url"]
    assert redacted["safe_id"] == raw["safe_id"]


@pytest.mark.t("T-38")
def test_redaction_drops_secret_keys() -> None:
    raw = {"authorization": "Bearer secret", "event": "authz.denied"}
    redacted = redact_event_dict(raw)
    assert "authorization" not in redacted
    assert redacted["event"] == "authz.denied"


@pytest.mark.t("T-38")
def test_bare_token_key_is_redacted_but_input_tokens_kept() -> None:
    raw = {"token": "secret", "input_tokens": 7, "gen_ai.usage.input_tokens": 123}
    redacted = redact_event_dict(raw)
    assert redacted["token"] == "[redacted]"  # noqa: S105
    assert redacted["input_tokens"] == 7
    assert redacted["gen_ai.usage.input_tokens"] == 123


@pytest.mark.t("T-38")
def test_gen_ai_token_counts_survive_redaction() -> None:
    raw = {"gen_ai.usage.input_tokens": 123, "access_token": "secret-value"}
    redacted = redact_event_dict(raw)
    assert redacted["gen_ai.usage.input_tokens"] == 123
    assert "access_token" not in redacted


@pytest.mark.t("T-38")
def test_redaction_can_be_disabled_for_unit_comparisons() -> None:
    raw = {"authorization": "Bearer secret"}
    assert redact_event_dict(raw, enabled=False) == raw
