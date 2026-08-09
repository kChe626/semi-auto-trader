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


def make_service(
    *,
    trade_executor: Mock | None = None,
    portfolio_manager: Mock | None = None,
    preflight_runner: Mock | None = None,
) -> tuple[
    DashboardApprovalService,
    Mock,
    Mock,
    Mock,
]:
    if trade_executor is None:
        trade_executor = Mock(
            name="trade-executor"
        )

    if portfolio_manager is None:
        portfolio_manager = Mock(
            name="portfolio-manager"
        )

        portfolio_manager.can_open_new_trade.return_value = (
            True,
            "",
        )

    if preflight_runner is None:
        preflight_runner = Mock(
            name="preflight-runner"
        )

        preflight_runner.return_value = PreflightResult(
            approved=True,
            reasons=[],
        )

    service = DashboardApprovalService(
        trade_executor=trade_executor,
        portfolio_manager=portfolio_manager,
        preflight_runner=preflight_runner,
    )

    return (
        service,
        trade_executor,
        portfolio_manager,
        preflight_runner,
    )


def test_approve_executes_ready_workflow_with_generated_trade_id(
) -> None:
    (
        service,
        trade_executor,
        portfolio_manager,
        preflight_runner,
    ) = make_service()

    submitted_order = Mock(
        name="submitted-order"
    )

    trade_executor.execute.return_value = (
        submitted_order
    )

    workflow = make_workflow()

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

    portfolio_manager\
        .can_open_new_trade\
        .assert_called_once_with()

    preflight_runner.assert_called_once_with(
        workflow.plan
    )

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

    assert executable_workflow.preflight.approved is True


def test_approve_preserves_existing_trade_id() -> None:
    (
        service,
        trade_executor,
        portfolio_manager,
        preflight_runner,
    ) = make_service()

    workflow = make_workflow(
        trade_id="existing-trade-456",
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

    portfolio_manager\
        .can_open_new_trade\
        .assert_called_once_with()

    preflight_runner.assert_called_once_with(
        workflow.plan
    )

    create_trade_id.assert_not_called()

    executable_workflow = (
        trade_executor.execute.call_args.args[0]
    )

    assert (
        executable_workflow.trade_id
        == "existing-trade-456"
    )


def test_approve_rejects_workflow_not_ready_for_approval(
) -> None:
    (
        service,
        trade_executor,
        portfolio_manager,
        preflight_runner,
    ) = make_service()

    workflow = make_workflow(
        ready_for_approval=False,
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

    portfolio_manager\
        .can_open_new_trade\
        .assert_not_called()

    preflight_runner.assert_not_called()
    trade_executor.execute.assert_not_called()


def test_approve_blocks_when_execution_disabled() -> None:
    (
        service,
        trade_executor,
        portfolio_manager,
        preflight_runner,
    ) = make_service()

    workflow = make_workflow()

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

    portfolio_manager\
        .can_open_new_trade\
        .assert_not_called()

    preflight_runner.assert_not_called()
    trade_executor.execute.assert_not_called()


def test_approve_rejects_non_workflow_result() -> None:
    (
        service,
        trade_executor,
        portfolio_manager,
        preflight_runner,
    ) = make_service()

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

    portfolio_manager\
        .can_open_new_trade\
        .assert_not_called()

    preflight_runner.assert_not_called()
    trade_executor.execute.assert_not_called()


def test_approve_blocks_when_portfolio_limit_reached() -> None:
    portfolio_manager = Mock(
        name="portfolio-manager"
    )

    portfolio_manager.can_open_new_trade.return_value = (
        False,
        "Maximum active trades (1) reached.",
    )

    (
        service,
        trade_executor,
        _,
        preflight_runner,
    ) = make_service(
        portfolio_manager=portfolio_manager,
    )

    workflow = make_workflow()

    with patch(
        "dashboard.dashboard_approval_service."
        "EXECUTION_ENABLED",
        True,
    ):
        with pytest.raises(
            RuntimeError,
            match=(
                "Trade blocked by portfolio limits: "
                "Maximum active trades"
            ),
        ):
            service.approve(
                workflow
            )

    portfolio_manager\
        .can_open_new_trade\
        .assert_called_once_with()

    preflight_runner.assert_not_called()
    trade_executor.execute.assert_not_called()


def test_approve_blocks_when_daily_loss_limit_reached() -> None:
    portfolio_manager = Mock(
        name="portfolio-manager"
    )

    portfolio_manager.can_open_new_trade.return_value = (
        False,
        (
            "Daily loss limit reached: "
            "P/L -$2,000.00, "
            "limit -$2,000.00."
        ),
    )

    (
        service,
        trade_executor,
        _,
        preflight_runner,
    ) = make_service(
        portfolio_manager=portfolio_manager,
    )

    workflow = make_workflow()

    with patch(
        "dashboard.dashboard_approval_service."
        "EXECUTION_ENABLED",
        True,
    ):
        with pytest.raises(
            RuntimeError,
            match=(
                "Trade blocked by portfolio limits: "
                "Daily loss limit reached"
            ),
        ):
            service.approve(
                workflow
            )

    portfolio_manager\
        .can_open_new_trade\
        .assert_called_once_with()

    preflight_runner.assert_not_called()
    trade_executor.execute.assert_not_called()


def test_approve_blocks_when_fresh_preflight_rejects() -> None:
    preflight_runner = Mock(
        name="preflight-runner"
    )

    preflight_runner.return_value = PreflightResult(
        approved=False,
        reasons=[
            "Market is closed.",
        ],
    )

    (
        service,
        trade_executor,
        portfolio_manager,
        _,
    ) = make_service(
        preflight_runner=preflight_runner,
    )

    workflow = make_workflow()

    with patch(
        "dashboard.dashboard_approval_service."
        "EXECUTION_ENABLED",
        True,
    ):
        with pytest.raises(
            RuntimeError,
            match=(
                "Trade blocked by fresh broker "
                "preflight: Market is closed"
            ),
        ):
            service.approve(
                workflow
            )

    portfolio_manager\
        .can_open_new_trade\
        .assert_called_once_with()

    preflight_runner.assert_called_once_with(
        workflow.plan
    )

    trade_executor.execute.assert_not_called()


def test_approve_uses_fresh_preflight_result_for_execution(
) -> None:
    fresh_preflight = PreflightResult(
        approved=True,
        reasons=[],
    )

    preflight_runner = Mock(
        name="preflight-runner",
        return_value=fresh_preflight,
    )

    (
        service,
        trade_executor,
        _,
        _,
    ) = make_service(
        preflight_runner=preflight_runner,
    )

    workflow = make_workflow()

    with (
        patch(
            "dashboard.dashboard_approval_service."
            "EXECUTION_ENABLED",
            True,
        ),
        patch(
            "dashboard.dashboard_approval_service."
            "create_trade_id",
            return_value="trade-789",
        ),
    ):
        service.approve(
            workflow
        )

    executable_workflow = (
        trade_executor.execute.call_args.args[0]
    )

    assert (
        executable_workflow.preflight
        is fresh_preflight
    )

    assert (
        executable_workflow.trade_id
        == "trade-789"
    )