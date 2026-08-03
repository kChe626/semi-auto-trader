from unittest.mock import Mock

from execution.order_lifecycle_service import (
    OrderLifecycleService,
)
from execution.sqlite_trade_repository import (
    SqliteTradeRepository,
)
from models.trade import (
    Trade,
    TradeStatus,
)


def test_restart_recovery_updates_persisted_trade_state(
    tmp_path,
) -> None:
    database_path = tmp_path / "trades.db"

    repository = SqliteTradeRepository(
        database_path
    )

    trade = Trade(
        trade_id="trade-123",
        symbol="AAPL",
        quantity=10,
        status=TradeStatus.SUBMITTED,
        entry_price=200.00,
        stop_price=195.00,
        target_price=210.00,
        parent_order_id="order-456",
    )

    # Simulate before restart:
    # trade was already saved
    repository.save(trade)

    broker_order = Mock()
    broker_order.status = "filled"

    broker = Mock()
    broker.get_order_by_id.return_value = (
        broker_order
    )

    lifecycle_service = OrderLifecycleService(
        broker=broker,
        repository=repository,
    )

    # Simulate application restart:
    # reload open trades and synchronize
    updated_trades = (
        lifecycle_service.sync_open_trades()
    )

    recovered_trade = repository.get(
        "trade-123"
    )

    assert len(updated_trades) == 1

    assert (
        recovered_trade.status
        is TradeStatus.FILLED
    )

    broker.get_order_by_id.assert_called_once_with(
        "order-456"
    )