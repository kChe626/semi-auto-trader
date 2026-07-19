from models.trade_signal import TradeSignal
from risk.signal_to_plan import create_trade_plan_from_signal


def test_create_buy_trade_plan_from_signal() -> None:
    signal = TradeSignal(
        symbol="NVDA",
        signal_type="BUY",
        price=100.00,
        reason="Test bullish signal",
    )

    plan = create_trade_plan_from_signal(
        signal=signal,
        account_equity=10_000.00,
        risk_percent=0.01,
        stop_loss_percent=0.02,
        reward_risk_ratio=2.0,
    )

    assert plan.symbol == "NVDA"
    assert plan.signal_type == "BUY"
    assert plan.entry_price == 100.00
    assert plan.stop_price == 98.00
    assert plan.target_price == 104.00
    assert plan.quantity == 50
    assert plan.total_risk == 100.00
    assert plan.risk_reward_ratio == 2.00


def test_create_sell_trade_plan_from_signal() -> None:
    signal = TradeSignal(
        symbol="NVDA",
        signal_type="SELL",
        price=100.00,
        reason="Test bearish signal",
    )

    plan = create_trade_plan_from_signal(
        signal=signal,
        account_equity=10_000.00,
        risk_percent=0.01,
        stop_loss_percent=0.02,
        reward_risk_ratio=2.0,
    )

    assert plan.symbol == "NVDA"
    assert plan.signal_type == "SELL"
    assert plan.entry_price == 100.00
    assert plan.stop_price == 102.00
    assert plan.target_price == 96.00
    assert plan.quantity == 50
    assert plan.total_risk == 100.00
    assert plan.risk_reward_ratio == 2.00