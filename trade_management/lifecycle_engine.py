from __future__ import annotations

from broker.position_monitor import PositionMonitor
from execution.order_lifecycle_service import (
    OrderLifecycleService,
)
from models.reconciliation import ReconciliationResult
from trade_management.exit_reconciler import ExitReconciler
from trade_management.position_reconciler import (
    PositionReconciler,
)
from trade_management.state_reconciler import (
    TradeStateReconciler,
)


class TradeLifecycleEngine:
    """
    Synchronizes broker orders and positions into
    the local trade journal and trade repository.
    """

    def __init__(
        self,
        monitor: PositionMonitor,
        order_reconciler: TradeStateReconciler,
        position_reconciler: PositionReconciler,
        exit_reconciler: ExitReconciler | None = None,
        order_lifecycle_service: OrderLifecycleService | None = None,
    ) -> None:
        self._monitor = monitor
        self._order_reconciler = order_reconciler
        self._position_reconciler = (
            position_reconciler
        )
        self._exit_reconciler = exit_reconciler
        self._order_lifecycle_service = (
            order_lifecycle_service
        )

    def synchronize(
        self,
        limit: int = 100,
    ) -> list[ReconciliationResult]:
        results: list[ReconciliationResult] = []

        if self._order_lifecycle_service is not None:
            (
                self._order_lifecycle_service
                .sync_open_trades()
            )

        orders = self._monitor.get_recent_orders(
            limit=limit
        )

        for order in orders:
            result = (
                self._order_reconciler
                .reconcile_order(order)
            )

            results.append(result)

        positions = (
            self._monitor.get_open_positions()
        )

        for position in positions:
            (
                self._position_reconciler
                .reconcile_position(position)
            )

        if self._exit_reconciler is not None:
            (
                self._exit_reconciler
                .reconcile_closed_positions(
                    positions
                )
            )

        return results