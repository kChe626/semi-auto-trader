from unittest.mock import MagicMock

from broker.order_executor import OrderExecutor
from models.trade_plan import TradePlan


def test_submit_order_calls_alpaca() -> None:
    client = MagicMock()

    executor = OrderExecutor(client)

    plan = TradePlan(
        symbol="META",
        signal_type="BUY",
        entry_price=100,
        stop_price=98,
        target_price=104,
        quantity=10,
        risk_per_share=2,
        reward_per_share=4,
        total_risk=20,
        risk_reward_ratio=2,
    )

    executor.submit_bracket_order(plan)

    client.submit_order.assert_called_once()