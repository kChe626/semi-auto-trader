from datetime import (
    datetime,
    timedelta,
    timezone,
)

import pytest

from analytics.monthly_performance import (
    MonthlyPerformanceCalculator,
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
        MonthlyPerformanceCalculator.calculate(
            []
        )
    )

    assert result == ()
    assert isinstance(result, tuple)


def test_single_trade_month() -> None:
    trade = make_trade(
        trade_id="trade-1",
        realized_pl=250.0,
        r_multiple=2.0,
        closed_at=utc_datetime(
            2026,
            7,
            10,
        ),
    )

    result = (
        MonthlyPerformanceCalculator.calculate(
            [trade]
        )
    )

    assert len(result) == 1

    month = result[0]

    assert month.year == 2026
    assert month.month == 7
    assert month.period == "2026-07"
    assert month.trade_count == 1
    assert month.winning_trades == 1
    assert month.losing_trades == 0
    assert month.breakeven_trades == 0
    assert month.win_rate == pytest.approx(
        1.0
    )
    assert month.net_realized_pl == (
        pytest.approx(250.0)
    )
    assert month.gross_profit == (
        pytest.approx(250.0)
    )
    assert month.gross_loss == (
        pytest.approx(0.0)
    )
    assert month.average_trade == (
        pytest.approx(250.0)
    )
    assert month.average_winner == (
        pytest.approx(250.0)
    )
    assert month.average_loser == (
        pytest.approx(0.0)
    )
    assert month.profit_factor is None
    assert month.total_r_multiple == (
        pytest.approx(2.0)
    )
    assert month.average_r_multiple == (
        pytest.approx(2.0)
    )
    assert month.best_trade_pl == (
        pytest.approx(250.0)
    )
    assert month.worst_trade_pl == (
        pytest.approx(250.0)
    )


def test_multiple_trades_calculate_monthly_metrics() -> None:
    trades = [
        make_trade(
            trade_id="trade-1",
            realized_pl=300.0,
            r_multiple=2.0,
            closed_at=utc_datetime(
                2026,
                7,
                5,
            ),
        ),
        make_trade(
            trade_id="trade-2",
            realized_pl=-100.0,
            r_multiple=-1.0,
            closed_at=utc_datetime(
                2026,
                7,
                10,
            ),
        ),
        make_trade(
            trade_id="trade-3",
            realized_pl=200.0,
            r_multiple=1.5,
            closed_at=utc_datetime(
                2026,
                7,
                15,
            ),
        ),
        make_trade(
            trade_id="trade-4",
            realized_pl=0.0,
            r_multiple=0.0,
            closed_at=utc_datetime(
                2026,
                7,
                20,
            ),
        ),
    ]

    result = (
        MonthlyPerformanceCalculator.calculate(
            trades
        )
    )

    month = result[0]

    assert month.trade_count == 4
    assert month.winning_trades == 2
    assert month.losing_trades == 1
    assert month.breakeven_trades == 1

    assert month.win_rate == pytest.approx(
        0.5
    )

    assert month.net_realized_pl == (
        pytest.approx(400.0)
    )

    assert month.gross_profit == (
        pytest.approx(500.0)
    )

    assert month.gross_loss == (
        pytest.approx(-100.0)
    )

    assert month.average_trade == (
        pytest.approx(100.0)
    )

    assert month.average_winner == (
        pytest.approx(250.0)
    )

    assert month.average_loser == (
        pytest.approx(-100.0)
    )

    assert month.profit_factor == (
        pytest.approx(5.0)
    )

    assert month.total_r_multiple == (
        pytest.approx(2.5)
    )

    assert month.average_r_multiple == (
        pytest.approx(0.625)
    )

    assert month.best_trade_pl == (
        pytest.approx(300.0)
    )

    assert month.worst_trade_pl == (
        pytest.approx(-100.0)
    )


def test_trades_are_grouped_by_calendar_month() -> None:
    trades = [
        make_trade(
            trade_id="june-1",
            realized_pl=100.0,
            r_multiple=1.0,
            closed_at=utc_datetime(
                2026,
                6,
                30,
            ),
        ),
        make_trade(
            trade_id="july-1",
            realized_pl=200.0,
            r_multiple=2.0,
            closed_at=utc_datetime(
                2026,
                7,
                1,
            ),
        ),
        make_trade(
            trade_id="july-2",
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
        MonthlyPerformanceCalculator.calculate(
            trades
        )
    )

    assert [
        month.period
        for month in result
    ] == [
        "2026-06",
        "2026-07",
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
            trade_id="trade-3",
            realized_pl=100.0,
            r_multiple=1.0,
            closed_at=utc_datetime(
                2026,
                7,
                1,
            ),
        ),
        make_trade(
            trade_id="trade-1",
            realized_pl=100.0,
            r_multiple=1.0,
            closed_at=utc_datetime(
                2025,
                12,
                1,
            ),
        ),
        make_trade(
            trade_id="trade-2",
            realized_pl=100.0,
            r_multiple=1.0,
            closed_at=utc_datetime(
                2026,
                1,
                1,
            ),
        ),
    ]

    result = (
        MonthlyPerformanceCalculator.calculate(
            trades
        )
    )

    assert [
        month.period
        for month in result
    ] == [
        "2025-12",
        "2026-01",
        "2026-07",
    ]


def test_same_month_in_different_years_is_separate() -> None:
    trades = [
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
        make_trade(
            trade_id="trade-2026",
            realized_pl=200.0,
            r_multiple=2.0,
            closed_at=utc_datetime(
                2026,
                7,
                1,
            ),
        ),
    ]

    result = (
        MonthlyPerformanceCalculator.calculate(
            trades
        )
    )

    assert len(result) == 2
    assert result[0].period == "2025-07"
    assert result[1].period == "2026-07"


def test_all_losing_month_has_zero_profit_factor() -> None:
    trades = [
        make_trade(
            trade_id="trade-1",
            realized_pl=-100.0,
            r_multiple=-1.0,
            closed_at=utc_datetime(
                2026,
                7,
                1,
            ),
        ),
        make_trade(
            trade_id="trade-2",
            realized_pl=-50.0,
            r_multiple=-0.5,
            closed_at=utc_datetime(
                2026,
                7,
                2,
            ),
        ),
    ]

    result = (
        MonthlyPerformanceCalculator.calculate(
            trades
        )
    )

    month = result[0]

    assert month.winning_trades == 0
    assert month.losing_trades == 2
    assert month.win_rate == pytest.approx(
        0.0
    )
    assert month.gross_profit == (
        pytest.approx(0.0)
    )
    assert month.gross_loss == (
        pytest.approx(-150.0)
    )
    assert month.average_winner == (
        pytest.approx(0.0)
    )
    assert month.average_loser == (
        pytest.approx(-75.0)
    )
    assert month.profit_factor == (
        pytest.approx(0.0)
    )


def test_all_breakeven_month() -> None:
    trades = [
        make_trade(
            trade_id="trade-1",
            realized_pl=0.0,
            r_multiple=0.0,
            closed_at=utc_datetime(
                2026,
                7,
                1,
            ),
        ),
        make_trade(
            trade_id="trade-2",
            realized_pl=0.0,
            r_multiple=0.0,
            closed_at=utc_datetime(
                2026,
                7,
                2,
            ),
        ),
    ]

    result = (
        MonthlyPerformanceCalculator.calculate(
            trades
        )
    )

    month = result[0]

    assert month.trade_count == 2
    assert month.winning_trades == 0
    assert month.losing_trades == 0
    assert month.breakeven_trades == 2
    assert month.win_rate == pytest.approx(
        0.0
    )
    assert month.net_realized_pl == (
        pytest.approx(0.0)
    )
    assert month.profit_factor == (
        pytest.approx(0.0)
    )
    assert month.best_trade_pl == (
        pytest.approx(0.0)
    )
    assert month.worst_trade_pl == (
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
                7,
                index,
            ),
        )
        for index in range(1, 4)
    )

    result = (
        MonthlyPerformanceCalculator.calculate(
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
        MonthlyPerformanceCalculator.calculate(
            [
                object(),
            ]  # type: ignore[list-item]
        )