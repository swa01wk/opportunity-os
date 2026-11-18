"""T-38: uvicorn access logs pass through redaction (SPEC-08 B9)."""

import json
import logging

import pytest
from structlog.stdlib import ProcessorFormatter

from opportunityos.telemetry.log import uvicorn_log_config


@pytest.mark.t("T-38")
def test_uvicorn_access_record_masks_signed_url_query() -> None:
    config = uvicorn_log_config()
    formatter = ProcessorFormatter(
        processor=config["formatters"]["plain"]["processor"],
        foreign_pre_chain=config["formatters"]["plain"]["foreign_pre_chain"],
    )
    record = logging.LogRecord(
        name="uvicorn.access",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg='GET /objects/file?X-Amz-Signature=deadbeef "HTTP/1.1" 200',
        args=(),
        exc_info=None,
    )
    line = formatter.format(record)
    payload = json.loads(line)
    text = json.dumps(payload)
    assert "deadbeef" not in text
