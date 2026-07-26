from datetime import datetime, timedelta, timezone

import pytest

from analytics.equity_curve import (
    EquityCurveCalculator,
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
    opened_at: datetime | None = None,
    closed_at: datetime | None = None,
) -> ClosedTrade:
    normalized_opened_at = (
        opened_at
        if opened_at is not None
        else BASE_TIME
    )

    normalized_closed_at = (
        closed_at
        if closed_at is not None
        else normalized_opened_at
        + timedelta(hours=1)
    )

    holding_duration_seconds = (
        normalized_closed_at
        - normalized_opened_at
    ).total_seconds()

    return ClosedTrade(
        trade_id=trade_id,
        symbol=symbol,
        entry_price=200.0,
        exit_price=210.0,
        quantity=10.0,
        realized_pl=realized_pl,
        r_multiple=r_multiple,
        holding_duration_seconds=(
            holding_duration_seconds
        ),
        opened_at=normalized_opened_at,
        closed_at=normalized_closed_at,
    )


def test_empty_trade_collection_returns_flat_curve() -> None:
    curve = EquityCurveCalculator.calculate(
        [],
        starting_equity=100_000.0,
    )

    assert curve.starting_equity == pytest.approx(
        100_000.0
    )

    assert curve.ending_equity == pytest.approx(
        100_000.0
    )

    assert curve.total_realized_pl == pytest.approx(
        0.0
    )

    assert curve.points == ()


def test_single_winning_trade_increases_equity() -> None:
    trade = make_trade(
        realized_pl=250.0
    )

    curve = EquityCurveCalculator.calculate(
        [trade],
        starting_equity=100_000.0,
    )

    assert curve.ending_equity == pytest.approx(
        100_250.0
    )

    assert curve.total_realized_pl == pytest.approx(
        250.0
    )

    assert len(curve.points) == 1

    point = curve.points[0]

    assert point.trade_id == "trade-1"
    assert point.symbol == "AAPL"

    assert point.realized_pl == pytest.approx(
        250.0
    )

    assert point.cumulative_pl == pytest.approx(
        250.0
    )

    assert point.equity == pytest.approx(
        100_250.0
    )


def test_single_losing_trade_decreases_equity() -> None:
    trade = make_trade(
        realized_pl=-125.0
    )

    curve = EquityCurveCalculator.calculate(
        [trade],
        starting_equity=100_000.0,
    )

    assert curve.ending_equity == pytest.approx(
        99_875.0
    )

    assert curve.total_realized_pl == pytest.approx(
        -125.0
    )

    assert curve.points[0].equity == pytest.approx(
        99_875.0
    )


def test_multiple_trades_build_cumulative_curve() -> None:
    trades = [
        make_trade(
            trade_id="trade-1",
            realized_pl=100.0,
            closed_at=BASE_TIME
            + timedelta(hours=1),
        ),
        make_trade(
            trade_id="trade-2",
            realized_pl=-40.0,
            closed_at=BASE_TIME
            + timedelta(hours=2),
        ),
        make_trade(
            trade_id="trade-3",
            realized_pl=210.0,
            closed_at=BASE_TIME
            + timedelta(hours=3),
        ),
        make_trade(
            trade_id="trade-4",
            realized_pl=-80.0,
            closed_at=BASE_TIME
            + timedelta(hours=4),
        ),
    ]

    curve = EquityCurveCalculator.calculate(
        trades,
        starting_equity=100_000.0,
    )

    assert curve.total_realized_pl == pytest.approx(
        190.0
    )

    assert curve.ending_equity == pytest.approx(
        100_190.0
    )

    assert [
        point.cumulative_pl
        for point in curve.points
    ] == pytest.approx(
        [
            100.0,
            60.0,
            270.0,
            190.0,
        ]
    )

    assert [
        point.equity
        for point in curve.points
    ] == pytest.approx(
        [
            100_100.0,
            100_060.0,
            100_270.0,
            100_190.0,
        ]
    )


def test_trades_are_sorted_by_close_time() -> None:
    earlier_trade = make_trade(
        trade_id="trade-earlier",
        realized_pl=100.0,
        closed_at=BASE_TIME
        + timedelta(hours=1),
    )

    later_trade = make_trade(
        trade_id="trade-later",
        realized_pl=200.0,
        closed_at=BASE_TIME
        + timedelta(hours=2),
    )

    curve = EquityCurveCalculator.calculate(
        [
            later_trade,
            earlier_trade,
        ],
        starting_equity=100_000.0,
    )

    assert [
        point.trade_id
        for point in curve.points
    ] == [
        "trade-earlier",
        "trade-later",
    ]

    assert curve.points[0].equity == pytest.approx(
        100_100.0
    )

    assert curve.points[1].equity == pytest.approx(
        100_300.0
    )


def test_trade_id_breaks_equal_time_ties() -> None:
    same_close_time = (
        BASE_TIME
        + timedelta(hours=1)
    )

    trade_b = make_trade(
        trade_id="trade-b",
        realized_pl=200.0,
        closed_at=same_close_time,
    )

    trade_a = make_trade(
        trade_id="trade-a",
        realized_pl=100.0,
        closed_at=same_close_time,
    )

    curve = EquityCurveCalculator.calculate(
        [
            trade_b,
            trade_a,
        ],
        starting_equity=100_000.0,
    )

    assert [
        point.trade_id
        for point in curve.points
    ] == [
        "trade-a",
        "trade-b",
    ]


def test_breakeven_trade_leaves_equity_unchanged() -> None:
    trade = make_trade(
        realized_pl=0.0,
        r_multiple=0.0,
    )

    curve = EquityCurveCalculator.calculate(
        [trade],
        starting_equity=100_000.0,
    )

    assert curve.total_realized_pl == pytest.approx(
        0.0
    )

    assert curve.ending_equity == pytest.approx(
        100_000.0
    )

    assert curve.points[0].equity == pytest.approx(
        100_000.0
    )


def test_calculate_accepts_generator() -> None:
    trades = (
        make_trade(
            trade_id=f"trade-{index}",
            realized_pl=10.0,
            closed_at=BASE_TIME
            + timedelta(hours=index + 1),
        )
        for index in range(3)
    )

    curve = EquityCurveCalculator.calculate(
        trades,
        starting_equity=1_000.0,
    )

    assert len(curve.points) == 3

    assert curve.total_realized_pl == pytest.approx(
        30.0
    )

    assert curve.ending_equity == pytest.approx(
        1_030.0
    )


def test_result_points_are_immutable_tuple() -> None:
    curve = EquityCurveCalculator.calculate(
        [make_trade()],
        starting_equity=100_000.0,
    )

    assert isinstance(
        curve.points,
        tuple,
    )


@pytest.mark.parametrize(
    "starting_equity",
    [
        0.0,
        -1.0,
        -100_000.0,
    ],
)
def test_non_positive_starting_equity_is_rejected(
    starting_equity: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "starting_equity must be greater "
            "than zero"
        ),
    ):
        EquityCurveCalculator.calculate(
            [],
            starting_equity=starting_equity,
        )


@pytest.mark.parametrize(
    "starting_equity",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_non_finite_starting_equity_is_rejected(
    starting_equity: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="starting_equity must be finite",
    ):
        EquityCurveCalculator.calculate(
            [],
            starting_equity=starting_equity,
        )


def test_non_numeric_starting_equity_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="starting_equity must be numeric",
    ):
        EquityCurveCalculator.calculate(
            [],
            starting_equity="100000",  # type: ignore[arg-type]
        )