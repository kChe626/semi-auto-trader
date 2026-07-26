from __future__ import annotations

from database.trade_journal import TradeJournal
from models.broker_state import PositionSnapshot


class PositionReconciler:
    """
    Records newly detected broker positions in the trade journal.
    """

    def __init__(
        self,
        journal: TradeJournal,
    ) -> None:
        self._journal = journal

    def reconcile_position(
        self,
        position: PositionSnapshot,
    ) -> bool:
        symbol = position.symbol.strip().upper()

        if not symbol:
            raise ValueError("position symbol cannot be empty")

        latest = self._journal.get_latest_event_by_symbol(
            symbol
        )

        if latest is None:
            return False

        latest_status = str(
            latest.get("status", "")
        ).strip().lower()

        if latest_status in {
            "position_open",
            "position_closed",
        }:
            return False

        trade_id = latest.get("trade_id")

        if not trade_id:
            return False

        self._journal.record_event(
            symbol=symbol,
            asset_type=latest.get(
                "asset_type"
            )
            or "stock",
            signal_type=latest.get(
                "signal_type"
            ),
            score=latest.get("score"),
            entry_price=(
                position.average_entry_price
            ),
            stop_price=latest.get(
                "stop_price"
            ),
            target_price=latest.get(
                "target_price"
            ),
            quantity=position.quantity,
            total_risk=latest.get(
                "total_risk"
            ),
            risk_reward_ratio=latest.get(
                "risk_reward_ratio"
            ),
            status="position_open",
            reason="Broker position detected",
            trade_id=trade_id,
            order_id=latest.get(
                "order_id"
            ),
        )

        return True