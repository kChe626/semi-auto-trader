
import pytest

from models.trade_signal import TradeSignal
from risk.signal_to_plan import create_trade_plan_from_signal


def test_create_buy_trade_plan_from_signal() -> None:
    signal = TradeSignal(
        symbol="META",
        signal_type="BUY",
        price=100.0,
        reason="Bullish crossover",
    )

    plan = create_trade_plan_from_signal(
        signal=signal,
        account_equity=100_000.0,
        risk_percent=0.01,
        stop_loss_percent=0.02,
        reward_risk_ratio=2.0,
    )

    assert plan.symbol == "META"
    assert plan.signal_type == "BUY"
    assert plan.entry_price == pytest.approx(100.0)
    assert plan.stop_price == pytest.approx(98.0)
    assert plan.target_price == pytest.approx(104.0)

    assert plan.risk_per_share == pytest.approx(2.0)
    assert plan.reward_per_share == pytest.approx(4.0)
    assert plan.risk_reward_ratio == pytest.approx(2.0)

    assert plan.quantity == 500
    assert plan.total_risk == pytest.approx(1_000.0)


def test_create_sell_trade_plan_from_signal() -> None:
    signal = TradeSignal(
        symbol="META",
        signal_type="SELL",
        price=100.0,
        reason="Bearish crossover",
    )

    plan = create_trade_plan_from_signal(
        signal=signal,
        account_equity=100_000.0,
        risk_percent=0.01,
        stop_loss_percent=0.02,
        reward_risk_ratio=2.0,
    )

    assert plan.symbol == "META"
    assert plan.signal_type == "SELL"
    assert plan.entry_price == pytest.approx(100.0)
    assert plan.stop_price == pytest.approx(102.0)
    assert plan.target_price == pytest.approx(96.0)

    assert plan.risk_per_share == pytest.approx(2.0)
    assert plan.reward_per_share == pytest.approx(4.0)
    assert plan.risk_reward_ratio == pytest.approx(2.0)

    assert plan.quantity == 500
    assert plan.total_risk == pytest.approx(1_000.0)


def test_signal_metrics_are_copied_to_trade_plan() -> None:
    signal = TradeSignal(
        symbol="NVDA",
        signal_type="BUY",
        price=100.0,
        reason="Bullish crossover",
        rsi=55.0,
        short_sma=101.0,
        long_sma=100.0,
    )

    plan = create_trade_plan_from_signal(
        signal=signal,
        account_equity=100_000.0,
        risk_percent=0.01,
        stop_loss_percent=0.02,
        reward_risk_ratio=2.0,
    )

    assert plan.rsi == pytest.approx(55.0)
    assert plan.short_sma == pytest.approx(101.0)
    assert plan.long_sma == pytest.approx(100.0)


def test_create_buy_trade_plan_uses_atr_levels() -> None:
    signal = TradeSignal(
        symbol="AAPL",
        signal_type="BUY",
        price=100.0,
        reason="Bullish crossover",
        atr=2.0,
        rsi=55.0,
        short_sma=105.0,
        long_sma=100.0,
    )

    plan = create_trade_plan_from_signal(
        signal=signal,
        account_equity=100_000.0,
        risk_percent=0.01,
        atr_multiplier=2.0,
        reward_risk_ratio=2.0,
    )

    assert plan.stop_price == pytest.approx(96.0)
    assert plan.target_price == pytest.approx(108.0)

    assert plan.risk_per_share == pytest.approx(4.0)
    assert plan.reward_per_share == pytest.approx(8.0)
    assert plan.risk_reward_ratio == pytest.approx(2.0)

    assert plan.quantity == 250
    assert plan.total_risk == pytest.approx(1_000.0)


def test_create_sell_trade_plan_uses_atr_levels() -> None:
    signal = TradeSignal(
        symbol="AAPL",
        signal_type="SELL",
        price=100.0,
        reason="Bearish crossover",
        atr=2.0,
        rsi=45.0,
        short_sma=95.0,
        long_sma=100.0,
    )

    plan = create_trade_plan_from_signal(
        signal=signal,
        account_equity=100_000.0,
        risk_percent=0.01,
        atr_multiplier=2.0,
        reward_risk_ratio=2.0,
    )

    assert plan.stop_price == pytest.approx(104.0)
    assert plan.target_price == pytest.approx(92.0)

    assert plan.risk_per_share == pytest.approx(4.0)
    assert plan.reward_per_share == pytest.approx(8.0)
    assert plan.risk_reward_ratio == pytest.approx(2.0)

    assert plan.quantity == 250
    assert plan.total_risk == pytest.approx(1_000.0)


def test_create_trade_plan_rejects_missing_atr() -> None:
    signal = TradeSignal(
        symbol="AAPL",
        signal_type="BUY",
        price=100.0,
        reason="Bullish crossover",
    )

    with pytest.raises(ValueError, match="ATR"):
        create_trade_plan_from_signal(
            signal=signal,
            account_equity=100_000.0,
            risk_percent=0.01,
            atr_multiplier=2.0,
            reward_risk_ratio=2.0,
        )

