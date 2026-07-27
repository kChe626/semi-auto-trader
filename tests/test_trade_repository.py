from unittest.mock import Mock

import pytest

from execution.trade_repository import InMemoryTradeRepository
from models.trade import Trade, TradeStatus


def test_save_and_get_trade() -> None:
    repository = InMemoryTradeRepository()

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

    result = repository.get("trade-123")

    assert result is trade


def test_get_returns_none_when_trade_does_not_exist() -> None:
    repository = InMemoryTradeRepository()

    result = repository.get("missing-trade")

    assert result is None


def test_save_rejects_duplicate_trade_id() -> None:
    repository = InMemoryTradeRepository()

    first_trade = Trade(
        trade_id="trade-123",
        symbol="AAPL",
        quantity=10,
        status=TradeStatus.SUBMITTED,
        entry_price=200.00,
        stop_price=195.00,
        target_price=210.00,
        parent_order_id="order-1",
    )

    duplicate_trade = Trade(
        trade_id="trade-123",
        symbol="MSFT",
        quantity=5,
        status=TradeStatus.SUBMITTED,
        entry_price=400.00,
        stop_price=390.00,
        target_price=420.00,
        parent_order_id="order-2",
    )

    repository.save(first_trade)

    with pytest.raises(
        ValueError,
        match="trade already exists",
    ):
        repository.save(duplicate_trade)

    assert repository.get("trade-123") is first_trade


def test_get_all_returns_all_trades_in_save_order() -> None:
    repository = InMemoryTradeRepository()

    first_trade = Trade(
        trade_id="trade-123",
        symbol="AAPL",
        quantity=10,
        status=TradeStatus.SUBMITTED,
        entry_price=200.00,
        stop_price=195.00,
        target_price=210.00,
        parent_order_id="order-1",
    )

    second_trade = Trade(
        trade_id="trade-456",
        symbol="MSFT",
        quantity=5,
        status=TradeStatus.FILLED,
        entry_price=400.00,
        stop_price=390.00,
        target_price=420.00,
        parent_order_id="order-2",
    )

    repository.save(first_trade)
    repository.save(second_trade)

    result = repository.get_all()

    assert result == (
        first_trade,
        second_trade,
    )


def test_update_replaces_existing_trade() -> None:
    repository = InMemoryTradeRepository()

    original_trade = Trade(
        trade_id="trade-123",
        symbol="AAPL",
        quantity=10,
        status=TradeStatus.SUBMITTED,
        entry_price=200.00,
        stop_price=195.00,
        target_price=210.00,
        parent_order_id="order-1",
    )

    updated_trade = Trade(
        trade_id="trade-123",
        symbol="AAPL",
        quantity=10,
        status=TradeStatus.FILLED,
        entry_price=200.00,
        stop_price=195.00,
        target_price=210.00,
        parent_order_id="order-1",
    )

    repository.save(original_trade)
    repository.update(updated_trade)

    result = repository.get("trade-123")

    assert result is updated_trade
    assert result.status == TradeStatus.FILLED


def test_update_rejects_missing_trade() -> None:
    repository = InMemoryTradeRepository()

    trade = Mock()
    trade.trade_id = "trade-999"

    with pytest.raises(
        ValueError,
        match="trade does not exist",
    ):
        repository.update(trade)


def test_get_rejects_empty_trade_id() -> None:
    repository = InMemoryTradeRepository()

    with pytest.raises(
        ValueError,
        match="trade_id is required",
    ):
        repository.get("   ")


def test_get_open_returns_only_active_trades() -> None:
    repository = InMemoryTradeRepository()

    submitted_trade = Mock()
    submitted_trade.trade_id = "trade-123"
    submitted_trade.status = "SUBMITTED"

    filled_trade = Mock()
    filled_trade.trade_id = "trade-456"
    filled_trade.status = "FILLED"

    closed_trade = Mock()
    closed_trade.trade_id = "trade-789"
    closed_trade.status = "CLOSED"

    repository.save(submitted_trade)
    repository.save(filled_trade)
    repository.save(closed_trade)

    result = repository.get_open()

    assert result == (
        submitted_trade,
        filled_trade,
    )


def test_remove_deletes_existing_trade() -> None:
    repository = InMemoryTradeRepository()

    trade = Mock()
    trade.trade_id = "trade-123"
    trade.status = "CLOSED"

    repository.save(trade)
    repository.remove("trade-123")

    assert repository.get("trade-123") is None
    assert repository.get_all() == ()