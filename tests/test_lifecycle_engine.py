from unittest.mock import MagicMock

from models.reconciliation import ReconciliationResult
from trade_management.lifecycle_engine import (
    TradeLifecycleEngine,
)


def test_engine_reconciles_every_order_and_position() -> None:
    monitor = MagicMock()
    order_reconciler = MagicMock()
    position_reconciler = MagicMock()

    order1 = object()
    order2 = object()
    position1 = object()

    monitor.get_recent_orders.return_value = [
        order1,
        order2,
    ]
    monitor.get_open_positions.return_value = [
        position1,
    ]

    order_reconciler.reconcile_order.side_effect = [
        ReconciliationResult(
            order_id="1",
            symbol="AAPL",
            broker_status="filled",
            previous_status=None,
            recorded_status="order_filled",
            changed=True,
        ),
        ReconciliationResult(
            order_id="2",
            symbol="MSFT",
            broker_status="filled",
            previous_status=None,
            recorded_status="order_filled",
            changed=True,
        ),
    ]

    engine = TradeLifecycleEngine(
        monitor,
        order_reconciler,
        position_reconciler,
    )

    results = engine.synchronize()

    assert len(results) == 2

    monitor.get_recent_orders.assert_called_once_with(
        limit=100
    )
    monitor.get_open_positions.assert_called_once_with()

    assert order_reconciler.reconcile_order.call_count == 2

    position_reconciler.reconcile_position.assert_called_once_with(
        position1
    )


def test_engine_handles_no_orders_or_positions() -> None:
    monitor = MagicMock()
    order_reconciler = MagicMock()
    position_reconciler = MagicMock()

    monitor.get_recent_orders.return_value = []
    monitor.get_open_positions.return_value = []

    engine = TradeLifecycleEngine(
        monitor,
        order_reconciler,
        position_reconciler,
    )

    results = engine.synchronize()

    assert results == []

    order_reconciler.reconcile_order.assert_not_called()
    position_reconciler.reconcile_position.assert_not_called()

def test_engine_synchronizes_persisted_open_trades() -> None:
    monitor = MagicMock()
    order_reconciler = MagicMock()
    position_reconciler = MagicMock()
    order_lifecycle_service = MagicMock()

    monitor.get_recent_orders.return_value = []
    monitor.get_open_positions.return_value = []

    engine = TradeLifecycleEngine(
        monitor,
        order_reconciler,
        position_reconciler,
        order_lifecycle_service=order_lifecycle_service,
    )

    engine.synchronize()

    order_lifecycle_service.sync_open_trades.assert_called_once_with()

def test_engine_reconciles_closed_positions() -> None:
    monitor = MagicMock()
    order_reconciler = MagicMock()
    position_reconciler = MagicMock()
    exit_reconciler = MagicMock()

    position1 = object()
    position2 = object()

    monitor.get_recent_orders.return_value = []
    monitor.get_open_positions.return_value = [
        position1,
        position2,
    ]

    engine = TradeLifecycleEngine(
        monitor,
        order_reconciler,
        position_reconciler,
        exit_reconciler=exit_reconciler,
    )

    engine.synchronize()

    assert (
        position_reconciler
        .reconcile_position
        .call_args_list
        == [
            ((position1,),),
            ((position2,),),
        ]
    )

    (
        exit_reconciler
        .reconcile_closed_positions
        .assert_called_once_with(
            [
                position1,
                position2,
            ]
        )
    )
def test_engine_manages_every_open_position() -> None:
    monitor = MagicMock()
    order_reconciler = MagicMock()
    position_reconciler = MagicMock()
    position_management_coordinator = MagicMock()

    position1 = object()
    position2 = object()

    monitor.get_recent_orders.return_value = []
    monitor.get_open_positions.return_value = [
        position1,
        position2,
    ]

    engine = TradeLifecycleEngine(
        monitor,
        order_reconciler,
        position_reconciler,
        position_management_coordinator=(
            position_management_coordinator
        ),
    )

    engine.synchronize()

    assert (
        position_management_coordinator
        .manage_position
        .call_args_list
        == [
            ((position1,),),
            ((position2,),),
        ]
    )