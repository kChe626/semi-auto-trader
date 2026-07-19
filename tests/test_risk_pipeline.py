from models.trade_signal import TradeSignal
from risk.risk_manager import RiskManager
from risk.signal_to_plan import create_trade_plan_from_signal


def test_signal_plan_is_capped_by_risk_manager() -> None:
    signal = TradeSignal(
        symbol="META",
        signal_type="BUY",
        price=646.01,
        reason="Test signal",
    )

    plan = create_trade_plan_from_signal(
        signal=signal,
        account_equity=100_000,
        risk_percent=0.01,
        stop_loss_percent=0.02,
        reward_risk_ratio=2.0,
    )

    manager = RiskManager(
        account_equity=100_000,
        max_position_percent=0.10,
    )

    final_plan = manager.apply_position_limit(plan)

    assert final_plan.quantity == 15
    assert final_plan.entry_price * final_plan.quantity <= 10_000
    assert final_plan.total_risk < 1_000