import pytest

from unittest.mock import Mock

from execution.order_lifecycle_service import (
    OrderLifecycleService,
)
from models.trade import Trade, TradeStatus


def _make_trade() -> Trade:
    return Trade(
        trade_id="trade-123",
        symbol="AAPL",
        quantity=10,
        status=TradeStatus.SUBMITTED,
        entry_price=200.00,
        stop_price=195.00,
        target_price=210.00,
        parent_order_id="order-123",
    )


def test_sync_trade_updates_trade_status_from_broker() -> None:
    trade = _make_trade()

    broker_order = Mock()
    broker_order.status = "filled"

    broker = Mock()
    broker.get_order_by_id.return_value = broker_order

    repository = Mock()

    service = OrderLifecycleService(
        broker=broker,
        repository=repository,
    )

    result = service.sync_trade(trade)

    broker.get_order_by_id.assert_called_once_with(
        "order-123"
    )

    repository.update.assert_called_once()

    updated_trade = repository.update.call_args.args[0]

    assert updated_trade.trade_id == trade.trade_id
    assert updated_trade.symbol == trade.symbol
    assert updated_trade.quantity == trade.quantity
    assert updated_trade.status is TradeStatus.FILLED
    assert updated_trade.entry_price == trade.entry_price
    assert updated_trade.stop_price == trade.stop_price
    assert updated_trade.target_price == trade.target_price
    assert (
        updated_trade.parent_order_id
        == trade.parent_order_id
    )

    assert result == updated_trade

def test_sync_trade_does_not_update_repository_when_status_is_unchanged() -> None:
    trade = _make_trade()

    broker_order = Mock()
    broker_order.status = "accepted"

    broker = Mock()
    broker.get_order_by_id.return_value = broker_order

    repository = Mock()

    service = OrderLifecycleService(
        broker=broker,
        repository=repository,
    )

    result = service.sync_trade(trade)

    assert result is trade
    repository.update.assert_not_called()

def test_sync_trade_rejects_missing_parent_order_id() -> None:
    trade = Trade(
        trade_id="trade-123",
        symbol="AAPL",
        quantity=10,
        status=TradeStatus.SUBMITTED,
        entry_price=200.00,
        stop_price=195.00,
        target_price=210.00,
        parent_order_id="",
    )

    broker = Mock()
    repository = Mock()

    service = OrderLifecycleService(
        broker=broker,
        repository=repository,
    )

    with pytest.raises(
        ValueError,
        match="Parent order ID is required",
    ):
        service.sync_trade(trade)

    broker.get_order_by_id.assert_not_called()
    repository.update.assert_not_called()

def test_sync_trade_rejects_broker_order_without_status() -> None:
    trade = _make_trade()

    broker_order = Mock()
    broker_order.status = None

    broker = Mock()
    broker.get_order_by_id.return_value = broker_order

    repository = Mock()

    service = OrderLifecycleService(
        broker=broker,
        repository=repository,
    )

    with pytest.raises(
        ValueError,
        match="Broker order status is required",
    ):
        service.sync_trade(trade)

    repository.update.assert_not_called()

def test_sync_trade_rejects_missing_broker_order() -> None:
    trade = _make_trade()

    broker = Mock()
    broker.get_order_by_id.return_value = None

    repository = Mock()

    service = OrderLifecycleService(
        broker=broker,
        repository=repository,
    )

    with pytest.raises(
        ValueError,
        match="Broker order was not found",
    ):
        service.sync_trade(trade)

    repository.update.assert_not_called()

def test_sync_open_trades_synchronizes_each_open_trade() -> None:
    first_trade = _make_trade()

    second_trade = Trade(
        trade_id="trade-456",
        symbol="MSFT",
        quantity=5,
        status=TradeStatus.PARTIALLY_FILLED,
        entry_price=450.00,
        stop_price=440.00,
        target_price=470.00,
        parent_order_id="order-456",
    )

    repository = Mock()
    repository.get_open.return_value = [
        first_trade,
        second_trade,
    ]

    broker = Mock()

    service = OrderLifecycleService(
        broker=broker,
        repository=repository,
    )

    service.sync_trade = Mock(
        side_effect=[
            first_trade,
            second_trade,
        ]
    )

    result = service.sync_open_trades()

    repository.get_open.assert_called_once_with()

    assert service.sync_trade.call_args_list == [
        ((first_trade,),),
        ((second_trade,),),
    ]

    assert result == [
        first_trade,
        second_trade,
    ]