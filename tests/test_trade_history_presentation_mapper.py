from __future__ import annotations

from datetime import datetime, timezone

from analytics.performance_statistics import ClosedTrade
from dashboard.trade_history_presentation_mapper import (
    TradeHistoryPresentationMapper,
)


def make_trade() -> ClosedTrade:
    return ClosedTrade(
        trade_id="trade-1",
        symbol="aapl",
        entry_price=200.0,
        exit_price=205.0,
        quantity=10.0,
        realized_pl=50.0,
        r_multiple=1.25,
        holding_duration_seconds=90061.0,
        opened_at=datetime(
            2026,
            7,
            20,
            14,
            30,
            tzinfo=timezone.utc,
        ),
        closed_at=datetime(
            2026,
            7,
            21,
            15,
            31,
            1,
            tzinfo=timezone.utc,
        ),
    )


def test_map_returns_trade_history_section() -> None:
    mapper = TradeHistoryPresentationMapper()

    result = mapper.map((make_trade(),))

    assert result.has_rows is True
    assert len(result.rows) == 1


def test_trade_values_are_formatted() -> None:
    mapper = TradeHistoryPresentationMapper()

    result = mapper.map((make_trade(),))

    row = result.rows[0]

    assert row.trade_id == "trade-1"
    assert row.symbol == "AAPL"
    assert row.side == "LONG"
    assert row.opened_at == "2026-07-20 14:30 UTC"
    assert row.closed_at == "2026-07-21 15:31 UTC"
    assert row.quantity == "10"
    assert row.entry_price == "$200.00"
    assert row.exit_price == "$205.00"
    assert row.realized_profit_loss == "$50.00"
    assert row.r_multiple == "1.25R"
    assert row.holding_duration == "1d 1h 1m 1s"


def test_fractional_quantity_is_preserved() -> None:
    trade = ClosedTrade(
        trade_id="trade-2",
        symbol="msft",
        entry_price=400.0,
        exit_price=404.0,
        quantity=2.5,
        realized_pl=10.0,
        r_multiple=0.5,
        holding_duration_seconds=3600.0,
        opened_at=datetime(
            2026,
            7,
            22,
            14,
            30,
            tzinfo=timezone.utc,
        ),
        closed_at=datetime(
            2026,
            7,
            22,
            15,
            30,
            tzinfo=timezone.utc,
        ),
    )

    mapper = TradeHistoryPresentationMapper()

    result = mapper.map((trade,))

    assert result.rows[0].quantity == "2.5"


def test_negative_profit_loss_is_formatted() -> None:
    trade = ClosedTrade(
        trade_id="trade-3",
        symbol="nvda",
        entry_price=150.0,
        exit_price=145.0,
        quantity=10.0,
        realized_pl=-50.0,
        r_multiple=-1.0,
        holding_duration_seconds=1800.0,
        opened_at=datetime(
            2026,
            7,
            23,
            14,
            30,
            tzinfo=timezone.utc,
        ),
        closed_at=datetime(
            2026,
            7,
            23,
            15,
            0,
            tzinfo=timezone.utc,
        ),
    )

    mapper = TradeHistoryPresentationMapper()

    result = mapper.map((trade,))

    row = result.rows[0]

    assert row.realized_profit_loss == "-$50.00"
    assert row.r_multiple == "-1.00R"


def test_empty_trades_return_empty_section() -> None:
    mapper = TradeHistoryPresentationMapper()

    result = mapper.map(())

    assert result.rows == ()
    assert result.has_rows is False


def test_generator_input_is_supported() -> None:
    mapper = TradeHistoryPresentationMapper()

    result = mapper.map(
        trade
        for trade in (make_trade(),)
    )

    assert len(result.rows) == 1