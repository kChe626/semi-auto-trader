from types import SimpleNamespace
from unittest.mock import MagicMock

import main
from models.trade_plan import TradePlan

from pathlib import Path
from models.trade import TradeStatus


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


def configure_common_mocks(
    monkeypatch,
) -> tuple[MagicMock, MagicMock]:
    client = MagicMock()

    client.get_account.return_value = SimpleNamespace(
        equity="100000.00",
    )

    signal = SimpleNamespace(
        symbol="META",
        signal_type="BUY",
    )

    plan = create_test_plan()

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

    workflow = MagicMock()

    workflow.create_plan.return_value = plan

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

    monkeypatch.setattr(
        main,
        "run_broker_preflight",
        lambda **kwargs: SimpleNamespace(
            approved=True,
            reasons=[],
        ),
    )

    executor = MagicMock()

    monkeypatch.setattr(
        main,
        "OrderExecutor",
        lambda trading_client: executor,
    )

    monkeypatch.setattr(
        main,
        "verify_submitted_order",
        lambda **kwargs: SimpleNamespace(
            id="paper-order-123",
            symbol="META",
            status="accepted",
        ),
    )

    return client, executor


def test_main_stops_when_no_signals(
    monkeypatch,
    capsys,
) -> None:
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

    output = capsys.readouterr().out

    assert "No valid trade signals found." in output


def test_execution_disabled_never_submits_order(
    monkeypatch,
    capsys,
) -> None:
    _, executor = configure_common_mocks(
        monkeypatch
    )

    monkeypatch.setattr(
        main,
        "EXECUTION_ENABLED",
        False,
    )

    confirmation = MagicMock(
        return_value=True
    )

    monkeypatch.setattr(
        main,
        "confirm_paper_order",
        confirmation,
    )

    main.main()

    output = capsys.readouterr().out

    assert "Execution is disabled." in output

    confirmation.assert_not_called()

    executor.submit_bracket_order.assert_not_called()


def test_cancelled_confirmation_never_submits_order(
    monkeypatch,
    capsys,
) -> None:
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

    output = capsys.readouterr().out

    assert "cancelled" in output

    executor.submit_bracket_order.assert_not_called()

def test_main_uses_injected_trade_approval(
    monkeypatch,
) -> None:
    _, executor = configure_common_mocks(
        monkeypatch
    )

    monkeypatch.setattr(
        main,
        "EXECUTION_ENABLED",
        True,
    )

    executor.submit_bracket_order.return_value = (
        SimpleNamespace(
            id="paper-order-123",
            status="accepted",
        )
    )

    approval = MagicMock(
        return_value=True,
    )

    main.main(
        trade_approval=approval,
    )

    approval.assert_called_once()

    approved_plan = (
        approval
        .call_args
        .args[0]
    )

    assert approved_plan.symbol == "META"

    executor.submit_bracket_order.assert_called_once()


def test_confirmed_order_is_submitted_once(
    monkeypatch,
    capsys,
) -> None:
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

    output = capsys.readouterr().out

    executor.submit_bracket_order.assert_called_once()

    submitted_plan = (
        executor
        .submit_bracket_order
        .call_args
        .args[0]
    )

    assert submitted_plan.symbol == "META"

    assert (
        "PAPER ORDER SUBMITTED AND VERIFIED"
        in output
    )

    assert "paper-order-123" in output

def test_verified_order_is_saved_for_restart_recovery(
    monkeypatch,
) -> None:
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

    trade_repository = MagicMock()
    journal = MagicMock()

    main.main(
        trade_repository=trade_repository,
        journal=journal,
    )

    trade_repository.save.assert_called_once()

    saved_trade = (
        trade_repository
        .save
        .call_args
        .args[0]
    )

    assert saved_trade.symbol == "META"
    assert saved_trade.quantity > 0
    assert saved_trade.status is TradeStatus.SUBMITTED
    assert saved_trade.entry_price > 0
    assert saved_trade.stop_price > 0
    assert saved_trade.target_price > 0
    assert (
        saved_trade.parent_order_id
        == "paper-order-123"
    )


def test_synchronize_broker_state_wires_order_lifecycle_service(
    monkeypatch,
) -> None:
    trading_client = MagicMock()
    journal = MagicMock()
    trade_repository = MagicMock()

    monitor = MagicMock()
    order_reconciler = MagicMock()
    position_reconciler = MagicMock()
    exit_reconciler = MagicMock()
    order_lifecycle_service = MagicMock()
    lifecycle_engine = MagicMock()
    trade_manager = MagicMock()

    monkeypatch.setattr(
        main,
        "PositionMonitor",
        MagicMock(return_value=monitor),
    )

    monkeypatch.setattr(
        main,
        "TradeStateReconciler",
        MagicMock(
            return_value=order_reconciler
        ),
    )

    monkeypatch.setattr(
        main,
        "PositionReconciler",
        MagicMock(
            return_value=position_reconciler
        ),
    )

    monkeypatch.setattr(
        main,
        "ExitReconciler",
        MagicMock(
            return_value=exit_reconciler
        ),
    )

    lifecycle_service_class = MagicMock(
        return_value=order_lifecycle_service
    )

    monkeypatch.setattr(
        main,
        "OrderLifecycleService",
        lifecycle_service_class,
    )

    lifecycle_engine_class = MagicMock(
        return_value=lifecycle_engine
    )

    monkeypatch.setattr(
        main,
        "TradeLifecycleEngine",
        lifecycle_engine_class,
    )

    trade_manager_class = MagicMock(
        return_value=trade_manager
    )

    monkeypatch.setattr(
        main,
        "TradeManager",
        trade_manager_class,
    )

    result = main.synchronize_broker_state(
        trading_client=trading_client,
        journal=journal,
        trade_repository=trade_repository,
        notification_sender=None,
    )

    assert result is True

    lifecycle_service_class.assert_called_once_with(
        broker=trading_client,
        repository=trade_repository,
    )

    lifecycle_engine_class.assert_called_once_with(
        monitor=monitor,
        order_reconciler=order_reconciler,
        position_reconciler=position_reconciler,
        exit_reconciler=exit_reconciler,
        order_lifecycle_service=(
            order_lifecycle_service
        ),
    )

    trade_manager_class.assert_called_once_with(
        lifecycle_engine
    )

    trade_manager.start_cycle.assert_called_once_with()

def test_main_passes_trade_repository_to_synchronization(
    monkeypatch,
) -> None:
    trading_client = MagicMock()
    trading_client.get_account.return_value = (
        SimpleNamespace(
            equity="100000.00",
        )
    )

    trade_repository = MagicMock()
    synchronize = MagicMock(
        return_value=False,
    )

    monkeypatch.setattr(
        main,
        "create_trading_client",
        lambda: trading_client,
    )

    monkeypatch.setattr(
        main,
        "synchronize_broker_state",
        synchronize,
    )

    main.main(
        trade_repository=trade_repository,
    )

    synchronize.assert_called_once_with(
        trading_client=trading_client,
        journal=None,
        notification_sender=None,
        trade_repository=trade_repository,
    )
def test_run_production_wires_persistent_dependencies(
    monkeypatch,
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "trades.db"

    journal = MagicMock()
    trade_repository = MagicMock()
    run_main = MagicMock()

    journal_class = MagicMock(
        return_value=journal,
    )
    repository_factory = MagicMock(
        return_value=trade_repository,
    )

    monkeypatch.setattr(
        main,
        "TradeJournal",
        journal_class,
    )

    monkeypatch.setattr(
        main,
        "create_trade_repository",
        repository_factory,
    )

    monkeypatch.setattr(
        main,
        "main",
        run_main,
    )

    main.run_production(
        database_path=database_path,
    )

    journal_class.assert_called_once_with(
        database_path=database_path,
    )

    repository_factory.assert_called_once_with(
        database_path=database_path,
    )

    run_main.assert_called_once_with(
        notification_sender=(
            main.send_telegram_message
        ),
        journal=journal,
        trade_repository=trade_repository,
    )

def test_main_uses_trade_approval_factory(
    monkeypatch,
) -> None:
    approval = MagicMock(
        return_value=True,
    )

    factory = MagicMock(
        return_value=approval,
    )

    monkeypatch.setattr(
        main,
        "create_trade_approval",
        factory,
    )

    main.main()

    factory.assert_called_once()