from models.trade_plan import TradePlan
from risk.risk_manager import RiskManager


def test_position_is_reduced() -> None:
    plan = TradePlan(
        symbol="META",
        signal_type="BUY",
        entry_price=646.01,
        stop_price=633.09,
        target_price=671.85,
        quantity=77,
        risk_per_share=12.92,
        reward_per_share=25.84,
        total_risk=994.84,
        risk_reward_ratio=2.0,
    )

    manager = RiskManager(
        account_equity=100_000,
        max_position_percent=0.10,
    )

    plan = manager.apply_position_limit(plan)

    assert plan.quantity == 15
    assert round(plan.total_risk, 2) == 193.80


def test_position_not_reduced() -> None:
    plan = TradePlan(
        symbol="AAPL",
        signal_type="BUY",
        entry_price=200,
        stop_price=196,
        target_price=208,
        quantity=20,
        risk_per_share=4,
        reward_per_share=8,
        total_risk=80,
        risk_reward_ratio=2,
    )

    manager = RiskManager(
        account_equity=100_000,
        max_position_percent=0.10,
    )

    plan = manager.apply_position_limit(plan)

    assert plan.quantity == 20