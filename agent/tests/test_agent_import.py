"""T-31: the agent package imports, so its test runner is exercised."""

import importlib

import pytest


@pytest.mark.t("T-31")
def test_package_imports() -> None:
    assert importlib.import_module("opportunityos_agent").__all__ == []
