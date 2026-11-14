"""T-31: the contracts package imports, so its test runner is exercised."""

import importlib

import pytest


@pytest.mark.t("T-31")
def test_package_imports() -> None:
    assert importlib.import_module("opportunityos_contracts").__all__ == []
