from types import SimpleNamespace
from unittest.mock import MagicMock

import main

from models.preflight_result import PreflightResult
from models.trade import TradeStatus
from models.trade_plan import TradePlan
from models.workflow_result import WorkflowResult


def create_test_plan() -> TradePlan:
    return TradePlan(
        symbol="META",
        signal_type="BUY",
        entry_price=100.00,
        stop_price=98.00,
        target_price=104.00,
        quantity=10,
        risk_per_share=2.00,
        reward_per_share=4.00,
        total_risk=20.00,
        risk_reward_ratio=2.00,
    )


def configure_common_mocks(monkeypatch):
    client = MagicMock()

    client.get_account.return_value = SimpleNamespace(
        equity="100000.00",
    )

    signal = SimpleNamespace(
        symbol="META",
        signal_type="BUY",
    )

    workflow = MagicMock()

    workflow.prepare_trade.return_value = WorkflowResult(
        ready_for_approval=True,
        plan=create_test_plan(),
        preflight=PreflightResult(
            approved=True,
            reasons=[],
        ),
    )

    monkeypatch.setattr(
        main,
        "create_trading_client",
        lambda: client,
    )

    monkeypatch.setattr(
        main,
        "market_is_bullish",
        lambda: True,
    )

    monkeypatch.setattr(
        main,
        "scan_market",
        lambda: [signal],
    )

    monkeypatch.setattr(
        main,
        "TradeWorkflow",
        lambda **kwargs: workflow,
    )

    monkeypatch.setattr(
        main,
        "rank_trade_plans",
        lambda plans: [
            SimpleNamespace(
                plan=plans[0],
                score=85.0,
                reasons=[
                    "Qualified test candidate.",
                ],
            )
        ],
    )

    portfolio_manager = MagicMock()

    portfolio_manager.can_open_new_trade.return_value = (
        True,
        "",
    )

    monkeypatch.setattr(
        main,
        "PortfolioManager",
        lambda trading_client: portfolio_manager,
    )

    executor = MagicMock()

    monkeypatch.setattr(
        main,
        "OrderExecutor",
        lambda trading_client: executor,
    )

    return client, executor


def test_main_stops_when_no_signals(
    monkeypatch,
    capsys,
):
    client = MagicMock()

    client.get_account.return_value = SimpleNamespace(
        equity="100000.00",
    )

    monkeypatch.setattr(
        main,
        "create_trading_client",
        lambda: client,
    )

    monkeypatch.setattr(
        main,
        "market_is_bullish",
        lambda: True,
    )

    monkeypatch.setattr(
        main,
        "scan_market",
        lambda: [],
    )

    main.main()

    assert (
        "No valid trade signals found."
        in capsys.readouterr().out
    )


def test_execution_disabled_never_submits_order(
    monkeypatch,
):
    _, executor = configure_common_mocks(
        monkeypatch
    )

    monkeypatch.setattr(
        main,
        "EXECUTION_ENABLED",
        False,
    )

    main.main()

    executor.submit_bracket_order.assert_not_called()


def test_cancelled_confirmation_never_submits_order(
    monkeypatch,
):
    _, executor = configure_common_mocks(
        monkeypatch
    )

    monkeypatch.setattr(
        main,
        "EXECUTION_ENABLED",
        True,
    )

    monkeypatch.setattr(
        main,
        "confirm_paper_order",
        lambda plan: False,
    )

    main.main()

    executor.submit_bracket_order.assert_not_called()


def test_main_uses_injected_trade_approval(
    monkeypatch,
):
    configure_common_mocks(
        monkeypatch
    )

    monkeypatch.setattr(
        main,
        "EXECUTION_ENABLED",
        True,
    )

    approval = MagicMock(
        return_value=True,
    )

    main.main(
        trade_approval=approval,
    )

    approval.assert_called_once()


def test_confirmed_order_is_submitted_once(
    monkeypatch,
):
    _, executor = configure_common_mocks(
        monkeypatch
    )

    monkeypatch.setattr(
        main,
        "EXECUTION_ENABLED",
        True,
    )

    monkeypatch.setattr(
        main,
        "confirm_paper_order",
        lambda plan: True,
    )

    executor.submit_bracket_order.return_value = (
        SimpleNamespace(
            id="paper-order-123",
            status="accepted",
        )
    )

    main.main()

    executor.submit_bracket_order.assert_called_once()


def test_verified_order_is_saved_for_restart_recovery(
    monkeypatch,
):
    _, executor = configure_common_mocks(
        monkeypatch
    )

    monkeypatch.setattr(
        main,
        "EXECUTION_ENABLED",
        True,
    )

    monkeypatch.setattr(
        main,
        "synchronize_broker_state",
        lambda **kwargs: True,
    )

    monkeypatch.setattr(
        main,
        "confirm_paper_order",
        lambda plan: True,
    )

    executor.submit_bracket_order.return_value = (
        SimpleNamespace(
            id="paper-order-123",
            status="accepted",
        )
    )

    repository = MagicMock()
    journal = MagicMock()

    main.main(
        trade_repository=repository,
        journal=journal,
    )

    repository.save.assert_called_once()

    saved_trade = (
        repository.save.call_args.args[0]
    )

    assert (
        saved_trade.status
        == TradeStatus.SUBMITTED
    )


def test_synchronize_broker_state_returns_success(
):
    result = main.synchronize_broker_state(
        trading_client=MagicMock(),
        journal=MagicMock(),
        notification_sender=MagicMock(),
    )

    assert result is True


def test_synchronize_broker_state_accepts_trade_repository(
    monkeypatch,
):
    engine = MagicMock()

    monkeypatch.setattr(
        main,
        "TradeLifecycleEngine",
        lambda **kwargs: engine,
    )

    result = main.synchronize_broker_state(
        trading_client=MagicMock(),
        journal=MagicMock(),
        notification_sender=MagicMock(),
        trade_repository=MagicMock(),
    )

    assert result is True


def test_run_production_wires_persistent_dependencies(
    monkeypatch,
):
    called = {}

    monkeypatch.setattr(
        main,
        "TradeJournal",
        lambda **kwargs: "journal",
    )

    monkeypatch.setattr(
        main,
        "create_trade_repository",
        lambda **kwargs: "repository",
    )

    monkeypatch.setattr(
        main,
        "send_telegram_message",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main,
        "main",
        lambda **kwargs: called.update(kwargs),
    )

    main.run_production()

    assert (
        called["journal"]
        == "journal"
    )

    assert (
        called["trade_repository"]
        == "repository"
    )


def test_main_uses_trade_approval_factory(
    monkeypatch,
):
    configure_common_mocks(
        monkeypatch
    )

    monkeypatch.setattr(
        main,
        "EXECUTION_ENABLED",
        True,
    )

    approval = MagicMock(
        return_value=True,
    )

    monkeypatch.setattr(
        main,
        "create_trade_approval",
        lambda **kwargs: approval,
    )

    monkeypatch.setattr(
        main,
        "confirm_paper_order",
        lambda plan: True,
    )

    main.main()

    assert approval.called