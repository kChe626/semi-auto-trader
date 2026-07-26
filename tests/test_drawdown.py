from datetime import (
    datetime,
    timedelta,
    timezone,
)

import pytest

from analytics.drawdown import (
    DrawdownCalculator,
)
from analytics.equity_curve import (
    EquityCurve,
    EquityCurveCalculator,
    EquityCurvePoint,
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
    trade_id: str,
    realized_pl: float,
    closed_offset: int,
    symbol: str = "AAPL",
) -> ClosedTrade:
    opened_at = (
        BASE_TIME
        + timedelta(hours=closed_offset - 1)
    )

    closed_at = (
        BASE_TIME
        + timedelta(hours=closed_offset)
    )

    return ClosedTrade(
        trade_id=trade_id,
        symbol=symbol,
        entry_price=200.0,
        exit_price=210.0,
        quantity=10.0,
        realized_pl=realized_pl,
        r_multiple=realized_pl / 50.0,
        holding_duration_seconds=3600.0,
        opened_at=opened_at,
        closed_at=closed_at,
    )


def make_curve(
    realized_results: list[float],
    *,
    starting_equity: float = 100_000.0,
) -> EquityCurve:
    trades = [
        make_trade(
            trade_id=f"trade-{index + 1}",
            realized_pl=realized_pl,
            closed_offset=index + 1,
        )
        for index, realized_pl
        in enumerate(realized_results)
    ]

    return EquityCurveCalculator.calculate(
        trades,
        starting_equity=starting_equity,
    )


def test_empty_curve_has_zero_drawdown() -> None:
    curve = make_curve([])

    result = DrawdownCalculator.calculate(
        curve
    )

    assert result.starting_equity == pytest.approx(
        100_000.0
    )

    assert result.ending_equity == pytest.approx(
        100_000.0
    )

    assert result.peak_equity == pytest.approx(
        100_000.0
    )

    assert result.current_drawdown_amount == (
        pytest.approx(0.0)
    )

    assert result.current_drawdown_percent == (
        pytest.approx(0.0)
    )

    assert result.maximum_drawdown_amount == (
        pytest.approx(0.0)
    )

    assert result.maximum_drawdown_percent == (
        pytest.approx(0.0)
    )

    assert (
        result.maximum_drawdown_trade_id
        is None
    )

    assert result.recovered is True
    assert result.points == ()


def test_all_winning_trades_have_zero_drawdown() -> None:
    curve = make_curve(
        [
            100.0,
            200.0,
            300.0,
        ]
    )

    result = DrawdownCalculator.calculate(
        curve
    )

    assert result.peak_equity == pytest.approx(
        100_600.0
    )

    assert result.maximum_drawdown_amount == (
        pytest.approx(0.0)
    )

    assert result.maximum_drawdown_percent == (
        pytest.approx(0.0)
    )

    assert result.current_drawdown_amount == (
        pytest.approx(0.0)
    )

    assert result.recovered is True

    assert all(
        point.drawdown_amount == 0.0
        for point in result.points
    )


def test_losing_trade_creates_drawdown() -> None:
    curve = make_curve(
        [
            500.0,
            -200.0,
        ]
    )

    result = DrawdownCalculator.calculate(
        curve
    )

    assert result.peak_equity == pytest.approx(
        100_500.0
    )

    assert result.maximum_drawdown_amount == (
        pytest.approx(-200.0)
    )

    assert result.maximum_drawdown_percent == (
        pytest.approx(
            -200.0 / 100_500.0
        )
    )

    assert (
        result.maximum_drawdown_trade_id
        == "trade-2"
    )

    assert result.current_drawdown_amount == (
        pytest.approx(-200.0)
    )

    assert result.recovered is False


def test_maximum_drawdown_tracks_peak_to_valley() -> None:
    curve = make_curve(
        [
            300.0,
            200.0,
            -300.0,
            -350.0,
            -130.0,
        ]
    )

    result = DrawdownCalculator.calculate(
        curve
    )

    assert result.peak_equity == pytest.approx(
        100_500.0
    )

    assert result.ending_equity == pytest.approx(
        99_720.0
    )

    assert result.maximum_drawdown_amount == (
        pytest.approx(-780.0)
    )

    assert result.maximum_drawdown_percent == (
        pytest.approx(
            -780.0 / 100_500.0
        )
    )

    assert (
        result.maximum_drawdown_trade_id
        == "trade-5"
    )

    assert result.current_drawdown_amount == (
        pytest.approx(-780.0)
    )

    assert result.recovered is False


def test_new_peak_resets_current_drawdown() -> None:
    curve = make_curve(
        [
            500.0,
            -300.0,
            500.0,
        ]
    )

    result = DrawdownCalculator.calculate(
        curve
    )

    assert result.peak_equity == pytest.approx(
        100_700.0
    )

    assert result.current_drawdown_amount == (
        pytest.approx(0.0)
    )

    assert result.current_drawdown_percent == (
        pytest.approx(0.0)
    )

    assert result.maximum_drawdown_amount == (
        pytest.approx(-300.0)
    )

    assert (
        result.maximum_drawdown_trade_id
        == "trade-2"
    )

    assert result.recovered is True


def test_breakeven_at_peak_is_not_drawdown() -> None:
    curve = make_curve(
        [
            100.0,
            0.0,
        ]
    )

    result = DrawdownCalculator.calculate(
        curve
    )

    assert result.points[1].peak_equity == (
        pytest.approx(100_100.0)
    )

    assert result.points[1].drawdown_amount == (
        pytest.approx(0.0)
    )

    assert result.points[1].drawdown_percent == (
        pytest.approx(0.0)
    )

    assert result.recovered is True


def test_drawdown_points_preserve_trade_order() -> None:
    curve = make_curve(
        [
            100.0,
            -25.0,
            50.0,
        ]
    )

    result = DrawdownCalculator.calculate(
        curve
    )

    assert [
        point.trade_id
        for point in result.points
    ] == [
        "trade-1",
        "trade-2",
        "trade-3",
    ]


def test_drawdown_point_contains_running_peak() -> None:
    curve = make_curve(
        [
            100.0,
            -40.0,
            200.0,
            -50.0,
        ]
    )

    result = DrawdownCalculator.calculate(
        curve
    )

    assert [
        point.peak_equity
        for point in result.points
    ] == pytest.approx(
        [
            100_100.0,
            100_100.0,
            100_260.0,
            100_260.0,
        ]
    )

    assert [
        point.drawdown_amount
        for point in result.points
    ] == pytest.approx(
        [
            0.0,
            -40.0,
            0.0,
            -50.0,
        ]
    )


def test_points_are_returned_as_tuple() -> None:
    curve = make_curve(
        [100.0]
    )

    result = DrawdownCalculator.calculate(
        curve
    )

    assert isinstance(
        result.points,
        tuple,
    )


def test_invalid_curve_type_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="curve must be an EquityCurve",
    ):
        DrawdownCalculator.calculate(
            object()  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "invalid_value",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_non_finite_curve_summary_is_rejected(
    invalid_value: float,
) -> None:
    curve = EquityCurve(
        starting_equity=100_000.0,
        ending_equity=invalid_value,
        total_realized_pl=0.0,
        points=(),
    )

    with pytest.raises(
        ValueError,
        match=(
            "equity curve values must be finite"
        ),
    ):
        DrawdownCalculator.calculate(
            curve
        )


def test_non_positive_starting_equity_is_rejected() -> None:
    curve = EquityCurve(
        starting_equity=0.0,
        ending_equity=0.0,
        total_realized_pl=0.0,
        points=(),
    )

    with pytest.raises(
        ValueError,
        match=(
            "starting equity must be greater "
            "than zero"
        ),
    ):
        DrawdownCalculator.calculate(
            curve
        )


def test_non_finite_point_value_is_rejected() -> None:
    curve = EquityCurve(
        starting_equity=100_000.0,
        ending_equity=100_000.0,
        total_realized_pl=0.0,
        points=(
            EquityCurvePoint(
                trade_id="trade-1",
                symbol="AAPL",
                closed_at=BASE_TIME,
                realized_pl=float("nan"),
                cumulative_pl=0.0,
                equity=100_000.0,
            ),
        ),
    )

    with pytest.raises(
        ValueError,
        match=(
            "equity curve point values "
            "must be finite"
        ),
    ):
        DrawdownCalculator.calculate(
            curve
        )