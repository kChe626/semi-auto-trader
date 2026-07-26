from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from alpaca.trading.enums import QueryOrderStatus

from broker.position_monitor import PositionMonitor


def test_get_account_returns_snapshot() -> None:
    client = MagicMock()
    client.get_account.return_value = (
        SimpleNamespace(
            status="ACTIVE",
            equity="100000",
            cash="50000",
            buying_power="200000",
            trading_blocked=False,
            account_blocked=False,
            shorting_enabled=True,
        )
    )

    monitor = PositionMonitor(client)
    account = monitor.get_account()

    assert account.status == "ACTIVE"
    assert account.equity == 100000.0
    assert account.cash == 50000.0
    assert account.buying_power == 200000.0
    assert account.trading_blocked is False
    assert account.account_blocked is False
    assert account.shorting_enabled is True


def test_get_open_positions_returns_snapshots() -> None:
    client = MagicMock()
    client.get_all_positions.return_value = [
        SimpleNamespace(
            symbol="aapl",
            qty="10",
            side="long",
            avg_entry_price="200",
            current_price="205",
            market_value="2050",
            unrealized_pl="50",
        )
    ]

    monitor = PositionMonitor(client)
    positions = monitor.get_open_positions()

    assert len(positions) == 1

    position = positions[0]

    assert position.symbol == "AAPL"
    assert position.quantity == 10.0
    assert position.side == "long"
    assert position.average_entry_price == 200.0
    assert position.current_price == 205.0
    assert position.market_value == 2050.0
    assert position.unrealized_profit_loss == 50.0


def test_get_open_orders_returns_snapshots() -> None:
    client = MagicMock()
    client.get_orders.return_value = [
        SimpleNamespace(
            id="order-123",
            symbol="nvda",
            status="new",
            side="buy",
            qty="5",
            filled_qty="0",
            filled_avg_price=None,
            order_class="bracket",
            submitted_at=None,
            filled_at=None,
            canceled_at=None,
        )
    ]

    monitor = PositionMonitor(client)
    orders = monitor.get_open_orders()

    assert len(orders) == 1

    order = orders[0]

    assert order.order_id == "order-123"
    assert order.symbol == "NVDA"
    assert order.status == "new"
    assert order.side == "buy"
    assert order.quantity == 5.0
    assert order.filled_quantity == 0.0
    assert order.filled_average_price is None
    assert order.order_class == "bracket"

    request = client.get_orders.call_args.kwargs[
        "filter"
    ]

    assert request.status == QueryOrderStatus.OPEN
    assert request.nested is True


def test_get_recent_orders_returns_all_statuses() -> None:
    client = MagicMock()
    client.get_orders.return_value = [
        SimpleNamespace(
            id="order-456",
            symbol="meta",
            status="filled",
            side="buy",
            qty="4",
            filled_qty="4",
            filled_avg_price="710.25",
            order_class="bracket",
            submitted_at="submitted",
            filled_at="filled",
            canceled_at=None,
        )
    ]

    monitor = PositionMonitor(client)
    orders = monitor.get_recent_orders(
        limit=25
    )

    assert len(orders) == 1

    order = orders[0]

    assert order.order_id == "order-456"
    assert order.symbol == "META"
    assert order.status == "filled"
    assert order.filled_quantity == 4.0
    assert order.filled_average_price == 710.25
    assert order.submitted_at == "submitted"
    assert order.filled_at == "filled"
    assert order.cancelled_at is None

    request = client.get_orders.call_args.kwargs[
        "filter"
    ]

    assert request.status == QueryOrderStatus.ALL
    assert request.limit == 25
    assert request.nested is True


@pytest.mark.parametrize(
    "limit, message",
    [
        (
            0,
            "limit must be greater than zero",
        ),
        (
            -1,
            "limit must be greater than zero",
        ),
        (
            501,
            "limit cannot exceed 500",
        ),
    ],
)
def test_get_recent_orders_rejects_invalid_limit(
    limit: int,
    message: str,
) -> None:
    monitor = PositionMonitor(
        MagicMock()
    )

    with pytest.raises(
        ValueError,
        match=message,
    ):
        monitor.get_recent_orders(
            limit=limit
        )