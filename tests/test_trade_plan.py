from models.trade_plan import TradePlan


def test_trade_plan_stores_trade_details() -> None:
    plan = TradePlan(
        symbol="NVDA",
        signal_type="BUY",
        entry_price=185.00,
        stop_price=180.00,
        target_price=195.00,
        quantity=20,
        risk_per_share=5.00,
        reward_per_share=10.00,
        total_risk=100.00,
        risk_reward_ratio=2.00,
    )

    assert plan.symbol == "NVDA"
    assert plan.signal_type == "BUY"
    assert plan.entry_price == 185.00
    assert plan.stop_price == 180.00
    assert plan.target_price == 195.00
    assert plan.quantity == 20
    assert plan.total_risk == 100.00
    assert plan.risk_reward_ratio == 2.00