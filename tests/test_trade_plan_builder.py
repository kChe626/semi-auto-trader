import pytest

from risk.trade_plan_builder import build_trade_plan


def test_build_buy_trade_plan() -> None:
    plan = build_trade_plan(
        symbol="NVDA",
        signal_type="BUY",
        account_equity=10_000.00,
        risk_percent=0.01,
        entry_price=100.00,
        stop_price=95.00,
        target_price=110.00,
    )

    assert plan.symbol == "NVDA"
    assert plan.signal_type == "BUY"
    assert plan.quantity == 20
    assert plan.risk_per_share == 5.00
    assert plan.reward_per_share == 10.00
    assert plan.total_risk == 100.00
    assert plan.risk_reward_ratio == 2.00


def test_build_sell_trade_plan() -> None:
    plan = build_trade_plan(
        symbol="NVDA",
        signal_type="SELL",
        account_equity=10_000.00,
        risk_percent=0.01,
        entry_price=100.00,
        stop_price=105.00,
        target_price=90.00,
    )

    assert plan.signal_type == "SELL"
    assert plan.quantity == 20
    assert plan.risk_per_share == 5.00
    assert plan.reward_per_share == 10.00
    assert plan.total_risk == 100.00
    assert plan.risk_reward_ratio == 2.00


def test_rejects_invalid_signal_type() -> None:
    with pytest.raises(
        ValueError,
        match="Signal type must be BUY or SELL",
    ):
        build_trade_plan(
            symbol="NVDA",
            signal_type="HOLD",
            account_equity=10_000.00,
            risk_percent=0.01,
            entry_price=100.00,
            stop_price=95.00,
            target_price=110.00,
        )


def test_rejects_invalid_buy_stop() -> None:
    with pytest.raises(
        ValueError,
        match="stop price must be below entry price",
    ):
        build_trade_plan(
            symbol="NVDA",
            signal_type="BUY",
            account_equity=10_000.00,
            risk_percent=0.01,
            entry_price=100.00,
            stop_price=101.00,
            target_price=110.00,
        )


def test_rejects_invalid_sell_target() -> None:
    with pytest.raises(
        ValueError,
        match="target price must be below entry price",
    ):
        build_trade_plan(
            symbol="NVDA",
            signal_type="SELL",
            account_equity=10_000.00,
            risk_percent=0.01,
            entry_price=100.00,
            stop_price=105.00,
            target_price=101.00,
        )