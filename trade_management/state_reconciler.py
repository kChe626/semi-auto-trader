from __future__ import annotations

from database.trade_journal import TradeJournal
from models.broker_state import OrderSnapshot
from models.reconciliation import ReconciliationResult


BROKER_STATUS_TO_JOURNAL_STATUS = {
    "new": "order_open",
    "accepted": "order_open",
    "pending_new": "order_open",
    "partially_filled": "order_partially_filled",
    "filled": "order_filled",
    "canceled": "order_cancelled",
    "expired": "order_expired",
    "rejected": "order_rejected",
}


class TradeStateReconciler:
    """
    Synchronizes broker order status into the trade journal.
    """

    def __init__(
        self,
        journal: TradeJournal,
    ) -> None:
        self._journal = journal

    def reconcile_order(
        self,
        order: OrderSnapshot,
    ) -> ReconciliationResult:
        latest = self._journal.get_latest_event_by_order_id(
            order.order_id
        )

        previous_status = (
            None
            if latest is None
            else latest["status"]
        )

        recorded_status = (
            BROKER_STATUS_TO_JOURNAL_STATUS.get(
                order.status.lower()
            )
        )

        changed = (
            recorded_status is not None
            and recorded_status != previous_status
        )

        if changed:
            self._journal.record_event(
                symbol=order.symbol,
                status=recorded_status,
                asset_type="stock",
                order_id=order.order_id,
            )

        return ReconciliationResult(
            order_id=order.order_id,
            symbol=order.symbol,
            broker_status=order.status,
            previous_status=previous_status,
            recorded_status=recorded_status,
            changed=changed,
        )