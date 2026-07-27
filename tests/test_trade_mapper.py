from uuid import UUID

from execution.trade_mapper import TradeMapper
from models.trade import Trade, TradeStatus
from models.trade_plan import TradePlan


def test_map_submitted_trade_creates_valid_trade() -> None:
    plan = TradePlan(
        symbol="AAPL",
        signal_type="BUY",
        entry_price=200.00,
        stop_price=195.00,
        target_price=210.00,
        quantity=10,
        risk_per_share=5.00,
        reward_per_share=10.00,
        total_risk=50.00,
        risk_reward_ratio=2.00,
    )

    trade = TradeMapper.map_submitted_trade(
        plan=plan,
        parent_order_id=(
            "12345678-1234-5678-1234-567812345678"
        ),
    )

    assert isinstance(trade, Trade)
    assert trade.symbol == "AAPL"
    assert trade.quantity == 10
    assert trade.status is TradeStatus.SUBMITTED
    assert trade.entry_price == 200.00
    assert trade.stop_price == 195.00
    assert trade.target_price == 210.00
    assert trade.parent_order_id == (
        "12345678-1234-5678-1234-567812345678"
    )

    UUID(trade.trade_id)