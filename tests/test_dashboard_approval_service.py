from unittest.mock import Mock
from models.trade_plan import TradePlan
from models.workflow_result import WorkflowResult

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


def test_approve_accepts_current_workflow_result() -> None:
    trade_executor = Mock()

    plan = TradePlan(
        symbol="AAPL",
        signal_type="BUY",
        entry_price=200.00,
        stop_price=195.00,
        target_price=210.00,
        quantity=10,
        risk_per_share=5.00,
        reward_per_share=10.00,
        total_risk=50.00,
        risk_reward_ratio=2.00,
    )

    workflow = WorkflowResult(
        ready_for_approval=True,
        plan=plan,
        preflight=Mock(),
    )

    submitted_order = Mock()
    trade_executor.execute.return_value = submitted_order

    service = DashboardApprovalService(
        trade_executor=trade_executor,
    )

    result = service.approve(workflow)

    assert result is submitted_order

    trade_executor.execute.assert_called_once_with(
        workflow
    )