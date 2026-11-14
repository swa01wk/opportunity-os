"""T-31: the contracts package imports, so its test runner is exercised."""

import pytest

from opportunityos_contracts import WorkflowRequest


@pytest.mark.t("T-31")
def test_package_exports_models() -> None:
    assert WorkflowRequest.model_fields["workflow_type"].alias == "workflowType"
