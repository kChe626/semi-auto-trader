from types import SimpleNamespace
from unittest.mock import MagicMock

import main
from models.trade_plan import TradePlan


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

    monkeypatch.setattr(
        main,
        "create_trade_plan_from_signal",
        lambda **kwargs: plan,
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