from unittest.mock import Mock, patch

import pytest

from dashboard.dashboard_approval_service import (
    DashboardApprovalService,
)
from models.preflight_result import PreflightResult
from models.trade_plan import TradePlan
from models.workflow_result import WorkflowResult


def make_plan() -> TradePlan:
    return TradePlan(
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


def make_workflow(
    *,
    ready_for_approval: bool = True,
    preflight_approved: bool = True,
    trade_id: str | None = None,
) -> WorkflowResult:
    return WorkflowResult(
        ready_for_approval=ready_for_approval,
        plan=make_plan(),
        preflight=PreflightResult(
            approved=preflight_approved,
            reasons=(
                []
                if preflight_approved
                else ["Market is closed."]
            ),
        ),
        trade_id=trade_id,
    )


def test_approve_executes_ready_workflow_with_generated_trade_id() -> None:
    trade_executor = Mock()

    submitted_order = Mock(
        name="submitted-order"
    )
    trade_executor.execute.return_value = (
        submitted_order
    )

    workflow = make_workflow()

    service = DashboardApprovalService(
        trade_executor=trade_executor,
    )

    with (
        patch(
            "dashboard.dashboard_approval_service."
            "EXECUTION_ENABLED",
            True,
        ),
        patch(
            "dashboard.dashboard_approval_service."
            "create_trade_id",
            return_value="trade-123",
        ),
    ):
        result = service.approve(
            workflow
        )

    assert result is submitted_order

    trade_executor.execute.assert_called_once()

    executable_workflow = (
        trade_executor.execute.call_args.args[0]
    )

    assert isinstance(
        executable_workflow,
        WorkflowResult,
    )
    assert (
        executable_workflow.trade_id
        == "trade-123"
    )
    assert (
        executable_workflow.plan
        is workflow.plan
    )


def test_approve_preserves_existing_trade_id() -> None:
    trade_executor = Mock()

    workflow = make_workflow(
        trade_id="existing-trade-456",
    )

    service = DashboardApprovalService(
        trade_executor=trade_executor,
    )

    with (
        patch(
            "dashboard.dashboard_approval_service."
            "EXECUTION_ENABLED",
            True,
        ),
        patch(
            "dashboard.dashboard_approval_service."
            "create_trade_id",
        ) as create_trade_id,
    ):
        service.approve(
            workflow
        )

    create_trade_id.assert_not_called()

    executable_workflow = (
        trade_executor.execute.call_args.args[0]
    )

    assert (
        executable_workflow.trade_id
        == "existing-trade-456"
    )


def test_approve_rejects_workflow_not_ready_for_approval() -> None:
    trade_executor = Mock()

    workflow = make_workflow(
        ready_for_approval=False,
    )

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
        service.approve(
            workflow
        )

    trade_executor.execute.assert_not_called()


def test_approve_rejects_failed_preflight() -> None:
    trade_executor = Mock()

    workflow = make_workflow(
        preflight_approved=False,
    )

    service = DashboardApprovalService(
        trade_executor=trade_executor,
    )

    with pytest.raises(
        ValueError,
        match=(
            "Trade workflow did not pass "
            "broker preflight"
        ),
    ):
        service.approve(
            workflow
        )

    trade_executor.execute.assert_not_called()


def test_approve_blocks_when_execution_disabled() -> None:
    trade_executor = Mock()

    workflow = make_workflow()

    service = DashboardApprovalService(
        trade_executor=trade_executor,
    )

    with patch(
        "dashboard.dashboard_approval_service."
        "EXECUTION_ENABLED",
        False,
    ):
        with pytest.raises(
            RuntimeError,
            match="Paper execution is disabled",
        ):
            service.approve(
                workflow
            )

    trade_executor.execute.assert_not_called()


def test_approve_rejects_non_workflow_result() -> None:
    trade_executor = Mock()

    service = DashboardApprovalService(
        trade_executor=trade_executor,
    )

    with pytest.raises(
        TypeError,
        match=(
            "Dashboard approval requires "
            "a WorkflowResult"
        ),
    ):
        service.approve(
            Mock()
        )

    trade_executor.execute.assert_not_called()