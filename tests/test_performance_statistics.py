from datetime import datetime, timedelta, timezone

import pytest

from analytics.performance_statistics import (
    PerformanceStatistics,
)
from models.closed_trade import ClosedTrade


BASE_TIME = datetime(
    2026,
    7,
    21,
    13,
    0,
    tzinfo=timezone.utc,
)


def make_trade(
    *,
    trade_id: str = "trade-1",
    symbol: str = "AAPL",
    realized_pl: float = 100.0,
    r_multiple: float = 2.0,
    holding_duration_seconds: float = 3600.0,
    entry_price: float = 200.0,
    exit_price: float = 210.0,
    quantity: float = 10.0,
) -> ClosedTrade:
    opened_at = BASE_TIME

    closed_at = opened_at + timedelta(
        seconds=holding_duration_seconds
    )

    return ClosedTrade(
        trade_id=trade_id,
        symbol=symbol,
        entry_price=entry_price,
        exit_price=exit_price,
        quantity=quantity,
        realized_pl=realized_pl,
        r_multiple=r_multiple,
        holding_duration_seconds=(
            holding_duration_seconds
        ),
        opened_at=opened_at,
        closed_at=closed_at,
    )


def test_empty_trade_collection_returns_zero_summary() -> None:
    summary = PerformanceStatistics.calculate([])

    assert summary.total_trades == 0
    assert summary.winners == 0
    assert summary.losers == 0
    assert summary.breakeven == 0

    assert summary.win_rate == 0.0
    assert summary.loss_rate == 0.0
    assert summary.breakeven_rate == 0.0

    assert summary.total_realized_pl == 0.0
    assert summary.average_realized_pl == 0.0
    assert summary.average_winner == 0.0
    assert summary.average_loser == 0.0
    assert summary.largest_winner == 0.0
    assert summary.largest_loser == 0.0

    assert summary.total_r == 0.0
    assert summary.average_r == 0.0
    assert summary.average_holding_duration_seconds == 0.0
    assert summary.expectancy == 0.0


def test_calculates_trade_counts() -> None:
    trades = [
        make_trade(
            trade_id="trade-1",
            realized_pl=100.0,
        ),
        make_trade(
            trade_id="trade-2",
            realized_pl=-50.0,
        ),
        make_trade(
            trade_id="trade-3",
            realized_pl=0.0,
        ),
    ]

    summary = PerformanceStatistics.calculate(trades)

    assert summary.total_trades == 3
    assert summary.winners == 1
    assert summary.losers == 1
    assert summary.breakeven == 1


def test_calculates_win_loss_and_breakeven_rates() -> None:
    trades = [
        make_trade(
            trade_id="trade-1",
            realized_pl=100.0,
        ),
        make_trade(
            trade_id="trade-2",
            realized_pl=50.0,
        ),
        make_trade(
            trade_id="trade-3",
            realized_pl=-25.0,
        ),
        make_trade(
            trade_id="trade-4",
            realized_pl=0.0,
        ),
    ]

    summary = PerformanceStatistics.calculate(trades)

    assert summary.win_rate == pytest.approx(50.0)
    assert summary.loss_rate == pytest.approx(25.0)
    assert summary.breakeven_rate == pytest.approx(25.0)


def test_calculates_total_and_average_realized_pl() -> None:
    trades = [
        make_trade(
            trade_id="trade-1",
            realized_pl=100.0,
        ),
        make_trade(
            trade_id="trade-2",
            realized_pl=-50.0,
        ),
        make_trade(
            trade_id="trade-3",
            realized_pl=25.0,
        ),
    ]

    summary = PerformanceStatistics.calculate(trades)

    assert summary.total_realized_pl == pytest.approx(
        75.0
    )

    assert summary.average_realized_pl == pytest.approx(
        25.0
    )

    assert summary.expectancy == pytest.approx(
        25.0
    )


def test_calculates_average_winner_and_loser() -> None:
    trades = [
        make_trade(
            trade_id="trade-1",
            realized_pl=100.0,
        ),
        make_trade(
            trade_id="trade-2",
            realized_pl=200.0,
        ),
        make_trade(
            trade_id="trade-3",
            realized_pl=-50.0,
        ),
        make_trade(
            trade_id="trade-4",
            realized_pl=-100.0,
        ),
    ]

    summary = PerformanceStatistics.calculate(trades)

    assert summary.average_winner == pytest.approx(
        150.0
    )

    assert summary.average_loser == pytest.approx(
        -75.0
    )


def test_calculates_largest_winner_and_loser() -> None:
    trades = [
        make_trade(
            trade_id="trade-1",
            realized_pl=75.0,
        ),
        make_trade(
            trade_id="trade-2",
            realized_pl=250.0,
        ),
        make_trade(
            trade_id="trade-3",
            realized_pl=-25.0,
        ),
        make_trade(
            trade_id="trade-4",
            realized_pl=-125.0,
        ),
    ]

    summary = PerformanceStatistics.calculate(trades)

    assert summary.largest_winner == pytest.approx(
        250.0
    )

    assert summary.largest_loser == pytest.approx(
        -125.0
    )


def test_calculates_total_and_average_r() -> None:
    trades = [
        make_trade(
            trade_id="trade-1",
            r_multiple=2.0,
        ),
        make_trade(
            trade_id="trade-2",
            r_multiple=-1.0,
        ),
        make_trade(
            trade_id="trade-3",
            r_multiple=0.5,
        ),
    ]

    summary = PerformanceStatistics.calculate(trades)

    assert summary.total_r == pytest.approx(
        1.5
    )

    assert summary.average_r == pytest.approx(
        0.5
    )


def test_calculates_average_holding_duration() -> None:
    trades = [
        make_trade(
            trade_id="trade-1",
            holding_duration_seconds=3600.0,
        ),
        make_trade(
            trade_id="trade-2",
            holding_duration_seconds=7200.0,
        ),
        make_trade(
            trade_id="trade-3",
            holding_duration_seconds=1800.0,
        ),
    ]

    summary = PerformanceStatistics.calculate(trades)

    assert (
        summary.average_holding_duration_seconds
        == pytest.approx(4200.0)
    )


def test_all_winners_have_zero_loser_statistics() -> None:
    trades = [
        make_trade(
            trade_id="trade-1",
            realized_pl=100.0,
        ),
        make_trade(
            trade_id="trade-2",
            realized_pl=200.0,
        ),
    ]

    summary = PerformanceStatistics.calculate(trades)

    assert summary.average_loser == 0.0
    assert summary.largest_loser == 0.0


def test_all_losers_have_zero_winner_statistics() -> None:
    trades = [
        make_trade(
            trade_id="trade-1",
            realized_pl=-50.0,
        ),
        make_trade(
            trade_id="trade-2",
            realized_pl=-100.0,
        ),
    ]

    summary = PerformanceStatistics.calculate(trades)

    assert summary.average_winner == 0.0
    assert summary.largest_winner == 0.0


def test_breakeven_trades_are_not_winners_or_losers() -> None:
    trades = [
        make_trade(
            trade_id="trade-1",
            realized_pl=0.0,
        ),
        make_trade(
            trade_id="trade-2",
            realized_pl=0.0,
        ),
    ]

    summary = PerformanceStatistics.calculate(trades)

    assert summary.total_trades == 2
    assert summary.winners == 0
    assert summary.losers == 0
    assert summary.breakeven == 2

    assert summary.win_rate == 0.0
    assert summary.loss_rate == 0.0
    assert summary.breakeven_rate == pytest.approx(
        100.0
    )


def test_calculate_accepts_generator() -> None:
    trades = (
        make_trade(
            trade_id=f"trade-{index}",
            realized_pl=10.0,
        )
        for index in range(3)
    )

    summary = PerformanceStatistics.calculate(trades)

    assert summary.total_trades == 3

    assert summary.total_realized_pl == pytest.approx(
        30.0
    )


def test_closed_trade_normalizes_identity_fields() -> None:
    trade = ClosedTrade(
        trade_id="  trade-1  ",
        symbol=" aapl ",
        entry_price=200.0,
        exit_price=210.0,
        quantity=10.0,
        realized_pl=100.0,
        r_multiple=2.0,
        holding_duration_seconds=3600.0,
        opened_at=BASE_TIME,
        closed_at=BASE_TIME + timedelta(hours=1),
    )

    assert trade.trade_id == "trade-1"
    assert trade.symbol == "AAPL"


def test_closed_trade_rejects_empty_trade_id() -> None:
    with pytest.raises(
        ValueError,
        match="trade_id cannot be empty",
    ):
        make_trade(
            trade_id="   ",
        )


def test_closed_trade_rejects_empty_symbol() -> None:
    with pytest.raises(
        ValueError,
        match="symbol cannot be empty",
    ):
        make_trade(
            symbol="   ",
        )


@pytest.mark.parametrize(
    (
        "field_name",
        "field_value",
        "expected_message",
    ),
    [
        (
            "entry_price",
            0.0,
            "entry_price must be greater than zero",
        ),
        (
            "exit_price",
            0.0,
            "exit_price must be greater than zero",
        ),
        (
            "quantity",
            0.0,
            "quantity must be greater than zero",
        ),
        (
            "holding_duration_seconds",
            -1.0,
            (
                "holding_duration_seconds "
                "cannot be negative"
            ),
        ),
    ],
)
def test_closed_trade_rejects_invalid_values(
    field_name: str,
    field_value: float,
    expected_message: str,
) -> None:
    values = {
        "trade_id": "trade-1",
        "symbol": "AAPL",
        "entry_price": 200.0,
        "exit_price": 210.0,
        "quantity": 10.0,
        "realized_pl": 100.0,
        "r_multiple": 2.0,
        "holding_duration_seconds": 3600.0,
        "opened_at": BASE_TIME,
        "closed_at": BASE_TIME + timedelta(hours=1),
    }

    values[field_name] = field_value

    with pytest.raises(
        ValueError,
        match=expected_message,
    ):
        ClosedTrade(**values)


@pytest.mark.parametrize(
    "field_name",
    [
        "entry_price",
        "exit_price",
        "quantity",
        "realized_pl",
        "r_multiple",
        "holding_duration_seconds",
    ],
)
def test_closed_trade_rejects_non_finite_values(
    field_name: str,
) -> None:
    values = {
        "trade_id": "trade-1",
        "symbol": "AAPL",
        "entry_price": 200.0,
        "exit_price": 210.0,
        "quantity": 10.0,
        "realized_pl": 100.0,
        "r_multiple": 2.0,
        "holding_duration_seconds": 3600.0,
        "opened_at": BASE_TIME,
        "closed_at": BASE_TIME + timedelta(hours=1),
    }

    values[field_name] = float("nan")

    with pytest.raises(
        ValueError,
        match=f"{field_name} must be finite",
    ):
        ClosedTrade(**values)


def test_closed_trade_rejects_naive_open_time() -> None:
    with pytest.raises(
        ValueError,
        match="opened_at must be timezone-aware",
    ):
        ClosedTrade(
            trade_id="trade-1",
            symbol="AAPL",
            entry_price=200.0,
            exit_price=210.0,
            quantity=10.0,
            realized_pl=100.0,
            r_multiple=2.0,
            holding_duration_seconds=3600.0,
            opened_at=datetime(
                2026,
                7,
                21,
                13,
                0,
            ),
            closed_at=BASE_TIME + timedelta(hours=1),
        )


def test_closed_trade_rejects_naive_close_time() -> None:
    with pytest.raises(
        ValueError,
        match="closed_at must be timezone-aware",
    ):
        ClosedTrade(
            trade_id="trade-1",
            symbol="AAPL",
            entry_price=200.0,
            exit_price=210.0,
            quantity=10.0,
            realized_pl=100.0,
            r_multiple=2.0,
            holding_duration_seconds=3600.0,
            opened_at=BASE_TIME,
            closed_at=datetime(
                2026,
                7,
                21,
                14,
                0,
            ),
        )


def test_closed_trade_rejects_close_before_open() -> None:
    with pytest.raises(
        ValueError,
        match="closed_at cannot be before opened_at",
    ):
        ClosedTrade(
            trade_id="trade-1",
            symbol="AAPL",
            entry_price=200.0,
            exit_price=210.0,
            quantity=10.0,
            realized_pl=100.0,
            r_multiple=2.0,
            holding_duration_seconds=3600.0,
            opened_at=BASE_TIME,
            closed_at=BASE_TIME - timedelta(minutes=1),
        )