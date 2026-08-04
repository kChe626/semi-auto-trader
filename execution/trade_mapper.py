from __future__ import annotations

from models.trade import Trade, TradeStatus
from models.trade_plan import TradePlan


class TradeMapper:
    @staticmethod
    def map_submitted_trade(
        *,
        trade_id: str,
        plan: TradePlan,
        parent_order_id: str,
    ) -> Trade:
        normalized_trade_id = str(
            trade_id
        ).strip()

        if not normalized_trade_id:
            raise ValueError(
                "trade_id is required"
            )

        return Trade(
            trade_id=normalized_trade_id,
            symbol=plan.symbol,
            quantity=plan.quantity,
            status=TradeStatus.SUBMITTED,
            entry_price=plan.entry_price,
            stop_price=plan.stop_price,
            target_price=plan.target_price,
            parent_order_id=parent_order_id,
        )