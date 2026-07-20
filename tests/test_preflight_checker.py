from models.trade_plan import TradePlan
from risk.preflight_checker import check_trade_preflight


def create_test_plan(quantity: int = 10) -> TradePlan:
    return TradePlan(
        symbol="META",
        signal_type="BUY",
        entry_price=100.00,
        stop_price=98.00,
        target_price=104.00,
        quantity=quantity,
        risk_per_share=2.00,
        reward_per_share=4.00,
        total_risk=quantity * 2.00,
        risk_reward_ratio=2.00,
    )


def test_preflight_approves_valid_trade() -> None:
    result = check_trade_preflight(
        create_test_plan(),
        market_is_open=True,
        buying_power=10_000.00,
        trading_blocked=False,
        has_existing_position=False,
        has_open_order=False,
    )

    assert result.approved is True
    assert result.reasons == []


def test_preflight_rejects_closed_market() -> None:
    result = check_trade_preflight(
        create_test_plan(),
        market_is_open=False,
        buying_power=10_000.00,
        trading_blocked=False,
        has_existing_position=False,
        has_open_order=False,
    )

    assert result.approved is False
    assert "Market is closed." in result.reasons


def test_preflight_rejects_blocked_account() -> None:
    result = check_trade_preflight(
        create_test_plan(),
        market_is_open=True,
        buying_power=10_000.00,
        trading_blocked=True,
        has_existing_position=False,
        has_open_order=False,
    )

    assert result.approved is False
    assert "Account is blocked from trading." in result.reasons


def test_preflight_rejects_zero_quantity() -> None:
    result = check_trade_preflight(
        create_test_plan(quantity=0),
        market_is_open=True,
        buying_power=10_000.00,
        trading_blocked=False,
        has_existing_position=False,
        has_open_order=False,
    )

    assert result.approved is False
    assert "Trade quantity must be greater than zero." in result.reasons


def test_preflight_rejects_insufficient_buying_power() -> None:
    result = check_trade_preflight(
        create_test_plan(),
        market_is_open=True,
        buying_power=500.00,
        trading_blocked=False,
        has_existing_position=False,
        has_open_order=False,
    )

    assert result.approved is False
    assert any(
        "Insufficient buying power" in reason
        for reason in result.reasons
    )


def test_preflight_rejects_existing_position() -> None:
    result = check_trade_preflight(
        create_test_plan(),
        market_is_open=True,
        buying_power=10_000.00,
        trading_blocked=False,
        has_existing_position=True,
        has_open_order=False,
    )

    assert result.approved is False
    assert any(
        "existing position" in reason
        for reason in result.reasons
    )


def test_preflight_rejects_open_order() -> None:
    result = check_trade_preflight(
        create_test_plan(),
        market_is_open=True,
        buying_power=10_000.00,
        trading_blocked=False,
        has_existing_position=False,
        has_open_order=True,
    )

    assert result.approved is False
    assert any(
        "open order" in reason
        for reason in result.reasons
    )


def test_preflight_returns_all_failed_rules() -> None:
    result = check_trade_preflight(
        create_test_plan(),
        market_is_open=False,
        buying_power=500.00,
        trading_blocked=True,
        has_existing_position=True,
        has_open_order=True,
    )

    assert result.approved is False
    assert len(result.reasons) == 5


def test_preflight_rejects_sell_when_shorting_disabled() -> None:
    plan = create_test_plan()
    plan.signal_type = "SELL"
    plan.stop_price = 102.00
    plan.target_price = 96.00

    result = check_trade_preflight(
        plan,
        market_is_open=True,
        buying_power=10_000.00,
        trading_blocked=False,
        has_existing_position=False,
        has_open_order=False,
    )

    assert result.approved is False
    assert "Short selling is disabled." in result.reasons


def test_preflight_rejects_unsupported_signal_type() -> None:
    plan = create_test_plan()
    plan.signal_type = "HOLD"

    result = check_trade_preflight(
        plan,
        market_is_open=True,
        buying_power=10_000.00,
        trading_blocked=False,
        has_existing_position=False,
        has_open_order=False,
    )

    assert result.approved is False
    assert "Unsupported signal type: HOLD." in result.reasons