from datetime import (
    datetime,
    timedelta,
    timezone,
)

import pytest

from analytics.yearly_performance import (
    YearlyPerformanceCalculator,
)
from models.closed_trade import ClosedTrade


def make_trade(
    *,
    trade_id: str,
    realized_pl: float,
    r_multiple: float,
    closed_at: datetime,
    symbol: str = "AAPL",
) -> ClosedTrade:
    opened_at = (
        closed_at - timedelta(hours=1)
    )

    return ClosedTrade(
        trade_id=trade_id,
        symbol=symbol,
        entry_price=100.0,
        exit_price=105.0,
        quantity=10.0,
        realized_pl=realized_pl,
        r_multiple=r_multiple,
        holding_duration_seconds=3600.0,
        opened_at=opened_at,
        closed_at=closed_at,
    )


def utc_datetime(
    year: int,
    month: int,
    day: int,
) -> datetime:
    return datetime(
        year,
        month,
        day,
        20,
        0,
        tzinfo=timezone.utc,
    )


def test_empty_trade_list_returns_empty_tuple() -> None:
    result = (
        YearlyPerformanceCalculator.calculate(
            []
        )
    )

    assert result == ()
    assert isinstance(result, tuple)


def test_single_trade_year() -> None:
    trade = make_trade(
        trade_id="trade-1",
        realized_pl=500.0,
        r_multiple=2.5,
        closed_at=utc_datetime(
            2026,
            7,
            10,
        ),
    )

    result = (
        YearlyPerformanceCalculator.calculate(
            [trade]
        )
    )

    assert len(result) == 1

    year = result[0]

    assert year.year == 2026
    assert year.period == "2026"
    assert year.trade_count == 1
    assert year.winning_trades == 1
    assert year.losing_trades == 0
    assert year.breakeven_trades == 0

    assert year.win_rate == pytest.approx(
        1.0
    )

    assert year.net_realized_pl == (
        pytest.approx(500.0)
    )

    assert year.gross_profit == (
        pytest.approx(500.0)
    )

    assert year.gross_loss == (
        pytest.approx(0.0)
    )

    assert year.average_trade == (
        pytest.approx(500.0)
    )

    assert year.average_winner == (
        pytest.approx(500.0)
    )

    assert year.average_loser == (
        pytest.approx(0.0)
    )

    assert year.profit_factor is None

    assert year.total_r_multiple == (
        pytest.approx(2.5)
    )

    assert year.average_r_multiple == (
        pytest.approx(2.5)
    )

    assert year.best_trade_pl == (
        pytest.approx(500.0)
    )

    assert year.worst_trade_pl == (
        pytest.approx(500.0)
    )


def test_multiple_trades_calculate_yearly_metrics() -> None:
    trades = [
        make_trade(
            trade_id="trade-1",
            realized_pl=400.0,
            r_multiple=2.0,
            closed_at=utc_datetime(
                2026,
                1,
                10,
            ),
        ),
        make_trade(
            trade_id="trade-2",
            realized_pl=-150.0,
            r_multiple=-1.0,
            closed_at=utc_datetime(
                2026,
                3,
                10,
            ),
        ),
        make_trade(
            trade_id="trade-3",
            realized_pl=250.0,
            r_multiple=1.5,
            closed_at=utc_datetime(
                2026,
                7,
                10,
            ),
        ),
        make_trade(
            trade_id="trade-4",
            realized_pl=0.0,
            r_multiple=0.0,
            closed_at=utc_datetime(
                2026,
                12,
                10,
            ),
        ),
    ]

    result = (
        YearlyPerformanceCalculator.calculate(
            trades
        )
    )

    year = result[0]

    assert year.trade_count == 4
    assert year.winning_trades == 2
    assert year.losing_trades == 1
    assert year.breakeven_trades == 1

    assert year.win_rate == pytest.approx(
        0.5
    )

    assert year.net_realized_pl == (
        pytest.approx(500.0)
    )

    assert year.gross_profit == (
        pytest.approx(650.0)
    )

    assert year.gross_loss == (
        pytest.approx(-150.0)
    )

    assert year.average_trade == (
        pytest.approx(125.0)
    )

    assert year.average_winner == (
        pytest.approx(325.0)
    )

    assert year.average_loser == (
        pytest.approx(-150.0)
    )

    assert year.profit_factor == (
        pytest.approx(
            650.0 / 150.0
        )
    )

    assert year.total_r_multiple == (
        pytest.approx(2.5)
    )

    assert year.average_r_multiple == (
        pytest.approx(0.625)
    )

    assert year.best_trade_pl == (
        pytest.approx(400.0)
    )

    assert year.worst_trade_pl == (
        pytest.approx(-150.0)
    )


def test_trades_are_grouped_by_calendar_year() -> None:
    trades = [
        make_trade(
            trade_id="trade-2025",
            realized_pl=100.0,
            r_multiple=1.0,
            closed_at=utc_datetime(
                2025,
                12,
                31,
            ),
        ),
        make_trade(
            trade_id="trade-2026-a",
            realized_pl=200.0,
            r_multiple=2.0,
            closed_at=utc_datetime(
                2026,
                1,
                1,
            ),
        ),
        make_trade(
            trade_id="trade-2026-b",
            realized_pl=-50.0,
            r_multiple=-0.5,
            closed_at=utc_datetime(
                2026,
                7,
                20,
            ),
        ),
    ]

    result = (
        YearlyPerformanceCalculator.calculate(
            trades
        )
    )

    assert [
        year.period
        for year in result
    ] == [
        "2025",
        "2026",
    ]

    assert result[0].trade_count == 1
    assert result[0].net_realized_pl == (
        pytest.approx(100.0)
    )

    assert result[1].trade_count == 2
    assert result[1].net_realized_pl == (
        pytest.approx(150.0)
    )


def test_results_are_sorted_chronologically() -> None:
    trades = [
        make_trade(
            trade_id="trade-2026",
            realized_pl=100.0,
            r_multiple=1.0,
            closed_at=utc_datetime(
                2026,
                7,
                1,
            ),
        ),
        make_trade(
            trade_id="trade-2024",
            realized_pl=100.0,
            r_multiple=1.0,
            closed_at=utc_datetime(
                2024,
                7,
                1,
            ),
        ),
        make_trade(
            trade_id="trade-2025",
            realized_pl=100.0,
            r_multiple=1.0,
            closed_at=utc_datetime(
                2025,
                7,
                1,
            ),
        ),
    ]

    result = (
        YearlyPerformanceCalculator.calculate(
            trades
        )
    )

    assert [
        year.year
        for year in result
    ] == [
        2024,
        2025,
        2026,
    ]


def test_multiple_months_in_same_year_are_combined() -> None:
    trades = [
        make_trade(
            trade_id="january",
            realized_pl=100.0,
            r_multiple=1.0,
            closed_at=utc_datetime(
                2026,
                1,
                1,
            ),
        ),
        make_trade(
            trade_id="july",
            realized_pl=200.0,
            r_multiple=2.0,
            closed_at=utc_datetime(
                2026,
                7,
                1,
            ),
        ),
        make_trade(
            trade_id="december",
            realized_pl=-50.0,
            r_multiple=-0.5,
            closed_at=utc_datetime(
                2026,
                12,
                1,
            ),
        ),
    ]

    result = (
        YearlyPerformanceCalculator.calculate(
            trades
        )
    )

    assert len(result) == 1
    assert result[0].year == 2026
    assert result[0].trade_count == 3
    assert result[0].net_realized_pl == (
        pytest.approx(250.0)
    )


def test_all_losing_year_has_zero_profit_factor() -> None:
    trades = [
        make_trade(
            trade_id="trade-1",
            realized_pl=-200.0,
            r_multiple=-1.0,
            closed_at=utc_datetime(
                2026,
                1,
                1,
            ),
        ),
        make_trade(
            trade_id="trade-2",
            realized_pl=-100.0,
            r_multiple=-0.5,
            closed_at=utc_datetime(
                2026,
                6,
                1,
            ),
        ),
    ]

    result = (
        YearlyPerformanceCalculator.calculate(
            trades
        )
    )

    year = result[0]

    assert year.winning_trades == 0
    assert year.losing_trades == 2
    assert year.win_rate == pytest.approx(
        0.0
    )

    assert year.gross_profit == (
        pytest.approx(0.0)
    )

    assert year.gross_loss == (
        pytest.approx(-300.0)
    )

    assert year.average_winner == (
        pytest.approx(0.0)
    )

    assert year.average_loser == (
        pytest.approx(-150.0)
    )

    assert year.profit_factor == (
        pytest.approx(0.0)
    )


def test_all_breakeven_year() -> None:
    trades = [
        make_trade(
            trade_id="trade-1",
            realized_pl=0.0,
            r_multiple=0.0,
            closed_at=utc_datetime(
                2026,
                1,
                1,
            ),
        ),
        make_trade(
            trade_id="trade-2",
            realized_pl=0.0,
            r_multiple=0.0,
            closed_at=utc_datetime(
                2026,
                12,
                1,
            ),
        ),
    ]

    result = (
        YearlyPerformanceCalculator.calculate(
            trades
        )
    )

    year = result[0]

    assert year.trade_count == 2
    assert year.winning_trades == 0
    assert year.losing_trades == 0
    assert year.breakeven_trades == 2

    assert year.win_rate == pytest.approx(
        0.0
    )

    assert year.net_realized_pl == (
        pytest.approx(0.0)
    )

    assert year.profit_factor == (
        pytest.approx(0.0)
    )

    assert year.best_trade_pl == (
        pytest.approx(0.0)
    )

    assert year.worst_trade_pl == (
        pytest.approx(0.0)
    )


def test_generator_input_is_supported() -> None:
    trades = (
        make_trade(
            trade_id=f"trade-{index}",
            realized_pl=100.0,
            r_multiple=1.0,
            closed_at=utc_datetime(
                2026,
                index,
                1,
            ),
        )
        for index in range(1, 4)
    )

    result = (
        YearlyPerformanceCalculator.calculate(
            trades
        )
    )

    assert len(result) == 1
    assert result[0].trade_count == 3


def test_invalid_trade_type_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "all trades must be "
            "ClosedTrade instances"
        ),
    ):
        YearlyPerformanceCalculator.calculate(
            [
                object(),
            ]  # type: ignore[list-item]
        )