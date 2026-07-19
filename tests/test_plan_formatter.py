from models.trade_plan import TradePlan
from risk.plan_formatter import format_trade_plan


def test_format_trade_plan() -> None:
    plan = TradePlan(
        symbol="NVDA",
        signal_type="BUY",
        entry_price=100.00,
        stop_price=98.00,
        target_price=104.00,
        quantity=50,
        risk_per_share=2.00,
        reward_per_share=4.00,
        total_risk=100.00,
        risk_reward_ratio=2.00,
    )

    output = format_trade_plan(plan)

    assert "TRADE PLAN: BUY NVDA" in output
    assert "Entry Price:       $100.00" in output
    assert "Stop Price:        $98.00" in output
    assert "Target Price:      $104.00" in output
    assert "Quantity:          50 shares" in output
    assert "Position Value:    $5,000.00" in output
    assert "Total Risk:        $100.00" in output
    assert "Risk/Reward Ratio: 2.00:1" in output