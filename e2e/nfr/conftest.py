"""Fixtures for the SPEC-01a static checks (T-31)."""

from pathlib import Path

import pytest

from nfr_support import ROOT, read_env_file


@pytest.fixture(scope="session")
def root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def image_pins() -> dict[str, str]:
    return read_env_file(ROOT / "infra" / "images.env")
