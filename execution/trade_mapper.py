from __future__ import annotations

from uuid import uuid4

from models.trade import Trade, TradeStatus
from models.trade_plan import TradePlan


class TradeMapper:
    @staticmethod
    def map_submitted_trade(
        *,
        plan: TradePlan,
        parent_order_id: str,
    ) -> Trade:
        return Trade(
            trade_id=str(uuid4()),
            symbol=plan.symbol,
            quantity=plan.quantity,
            status=TradeStatus.SUBMITTED,
            entry_price=plan.entry_price,
            stop_price=plan.stop_price,
            target_price=plan.target_price,
            parent_order_id=parent_order_id,
        )