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
def test_redaction_can_be_disabled_for_collector_tests() -> None:
    raw = {"authorization": "Bearer secret"}
    assert redact_event_dict(raw, enabled=False) == raw
