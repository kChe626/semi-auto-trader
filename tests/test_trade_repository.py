from unittest.mock import Mock

import pytest

from execution.trade_repository import InMemoryTradeRepository


def test_save_and_get_trade() -> None:
    repository = InMemoryTradeRepository()

    trade = Mock()
    trade.trade_id = "trade-123"

    repository.save(trade)

    result = repository.get("trade-123")

    assert result is trade


def test_get_returns_none_when_trade_does_not_exist() -> None:
    repository = InMemoryTradeRepository()

    result = repository.get("missing-trade")

    assert result is None


def test_save_rejects_empty_trade_id() -> None:
    repository = InMemoryTradeRepository()

    trade = Mock()
    trade.trade_id = "   "

    with pytest.raises(
        ValueError,
        match="trade_id is required",
    ):
        repository.save(trade)


def test_save_rejects_duplicate_trade_id() -> None:
    repository = InMemoryTradeRepository()

    first_trade = Mock()
    first_trade.trade_id = "trade-123"

    duplicate_trade = Mock()
    duplicate_trade.trade_id = "trade-123"

    repository.save(first_trade)

    with pytest.raises(
        ValueError,
        match="trade already exists",
    ):
        repository.save(duplicate_trade)

    assert repository.get("trade-123") is first_trade


def test_get_all_returns_all_trades_in_save_order() -> None:
    repository = InMemoryTradeRepository()

    first_trade = Mock()
    first_trade.trade_id = "trade-123"

    second_trade = Mock()
    second_trade.trade_id = "trade-456"

    repository.save(first_trade)
    repository.save(second_trade)

    result = repository.get_all()

    assert result == (
        first_trade,
        second_trade,
    )

def test_update_replaces_existing_trade() -> None:
    repository = InMemoryTradeRepository()

    original_trade = Mock()
    original_trade.trade_id = "trade-123"
    original_trade.status = "SUBMITTED"

    updated_trade = Mock()
    updated_trade.trade_id = "trade-123"
    updated_trade.status = "FILLED"

    repository.save(original_trade)

    repository.update(updated_trade)

    result = repository.get("trade-123")

    assert result is updated_trade
    assert result.status == "FILLED"

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