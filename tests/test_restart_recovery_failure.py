import pytest

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


def test_restart_recovery_rejects_missing_broker_order(
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

    repository.save(trade)

    broker = type(
        "Broker",
        (),
        {
            "get_order_by_id": lambda self, order_id: None
        },
    )()

    lifecycle_service = OrderLifecycleService(
        broker=broker,
        repository=repository,
    )

    with pytest.raises(
        ValueError,
        match="Broker order was not found",
    ):
        lifecycle_service.sync_open_trades()

    recovered_trade = repository.get(
        "trade-123"
    )

    assert recovered_trade.status is TradeStatus.SUBMITTED