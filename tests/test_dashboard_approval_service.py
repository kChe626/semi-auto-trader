from unittest.mock import Mock

import pytest

from dashboard.dashboard_approval_service import (
    DashboardApprovalService,
)


def test_approve_trade_submits_trade_plan() -> None:
    trade_executor = Mock()

    workflow = Mock()
    workflow.status = "READY FOR APPROVAL"

    service = DashboardApprovalService(
        trade_executor=trade_executor,
    )

    service.approve(workflow)

    trade_executor.execute.assert_called_once_with(
        workflow
    )


def test_approve_rejects_workflow_not_ready_for_approval() -> None:
    trade_executor = Mock()

    workflow = Mock()
    workflow.status = "REJECTED"

    service = DashboardApprovalService(
        trade_executor=trade_executor,
    )

    with pytest.raises(
        ValueError,
        match=(
            "Trade workflow is not ready "
            "for approval"
        ),
    ):
        service.approve(workflow)

    trade_executor.execute.assert_not_called()