import pytest

from models.trade import Trade, TradeStatus
from execution.sqlite_trade_repository import SqliteTradeRepository


def test_save_and_get_trade(tmp_path) -> None:
    database_path = tmp_path / "trades.db"

    repository = SqliteTradeRepository(database_path)

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

    assert result == trade

def test_save_rejects_duplicate_trade_id(tmp_path) -> None:
    database_path = tmp_path / "trades.db"

    repository = SqliteTradeRepository(database_path)

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

    with pytest.raises(ValueError):
        repository.save(trade)

def test_get_all_returns_all_trades_in_save_order(tmp_path) -> None:
    repository = SqliteTradeRepository(tmp_path / "trades.db")

    first_trade = Trade(
        trade_id="trade-1",
        symbol="AAPL",
        quantity=10,
        status=TradeStatus.SUBMITTED,
        entry_price=200.00,
        stop_price=195.00,
        target_price=210.00,
        parent_order_id="order-1",
    )
    second_trade = Trade(
        trade_id="trade-2",
        symbol="MSFT",
        quantity=5,
        status=TradeStatus.FILLED,
        entry_price=450.00,
        stop_price=440.00,
        target_price=470.00,
        parent_order_id="order-2",
    )

    repository.save(first_trade)
    repository.save(second_trade)

    assert repository.get_all() == [
        first_trade,
        second_trade,
    ]

def test_update_replaces_existing_trade(tmp_path) -> None:
    repository = SqliteTradeRepository(tmp_path / "trades.db")

    original_trade = Trade(
        trade_id="trade-123",
        symbol="AAPL",
        quantity=10,
        status=TradeStatus.SUBMITTED,
        entry_price=200.00,
        stop_price=195.00,
        target_price=210.00,
        parent_order_id="order-456",
    )
    updated_trade = Trade(
        trade_id="trade-123",
        symbol="AAPL",
        quantity=10,
        status=TradeStatus.FILLED,
        entry_price=201.00,
        stop_price=195.00,
        target_price=210.00,
        parent_order_id="order-456",
    )

    repository.save(original_trade)
    repository.update(updated_trade)

    assert repository.get("trade-123") == updated_trade

def test_update_rejects_missing_trade(tmp_path) -> None:
    repository = SqliteTradeRepository(tmp_path / "trades.db")

    trade = Trade(
        trade_id="missing-trade",
        symbol="MSFT",
        quantity=5,
        status=TradeStatus.SUBMITTED,
        entry_price=450.00,
        stop_price=440.00,
        target_price=470.00,
        parent_order_id="order-789",
    )

    with pytest.raises(
        ValueError,
        match="trade does not exist: missing-trade",
    ):
        repository.update(trade)

def test_remove_deletes_existing_trade(tmp_path) -> None:
    repository = SqliteTradeRepository(tmp_path / "trades.db")

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
    repository.remove("trade-123")

    assert repository.get("trade-123") is None

def test_remove_rejects_missing_trade(tmp_path) -> None:
    repository = SqliteTradeRepository(tmp_path / "trades.db")

    with pytest.raises(
        ValueError,
        match="trade does not exist: missing-trade",
    ):
        repository.remove("missing-trade")

def test_get_open_returns_only_active_trades(tmp_path) -> None:
    repository = SqliteTradeRepository(tmp_path / "trades.db")

    submitted_trade = Trade(
        trade_id="trade-1",
        symbol="AAPL",
        quantity=10,
        status=TradeStatus.SUBMITTED,
        entry_price=200.00,
        stop_price=195.00,
        target_price=210.00,
        parent_order_id="order-1",
    )
    filled_trade = Trade(
        trade_id="trade-2",
        symbol="MSFT",
        quantity=5,
        status=TradeStatus.FILLED,
        entry_price=450.00,
        stop_price=440.00,
        target_price=470.00,
        parent_order_id="order-2",
    )
    closed_trade = Trade(
        trade_id="trade-3",
        symbol="NVDA",
        quantity=3,
        status=TradeStatus.CLOSED,
        entry_price=120.00,
        stop_price=115.00,
        target_price=130.00,
        parent_order_id="order-3",
    )

    repository.save(submitted_trade)
    repository.save(filled_trade)
    repository.save(closed_trade)

    assert repository.get_open() == [
        submitted_trade,
        filled_trade,
    ]

def test_get_open_includes_partially_filled_trade(
    tmp_path,
) -> None:
    repository = SqliteTradeRepository(
        tmp_path / "trades.db"
    )

    partially_filled_trade = Trade(
        trade_id="trade-partial",
        symbol="AAPL",
        quantity=10,
        status=TradeStatus.PARTIALLY_FILLED,
        entry_price=200.00,
        stop_price=195.00,
        target_price=210.00,
        parent_order_id="order-partial",
    )

    repository.save(
        partially_filled_trade
    )

    assert repository.get_open() == [
        partially_filled_trade
    ]