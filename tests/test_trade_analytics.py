from datetime import datetime, timedelta, timezone

import pytest

from trade_management.trade_analytics import (
    TradeAnalytics,
    TradeResult,
)


def make_entry_time() -> datetime:
    return datetime(
        2026,
        7,
        20,
        14,
        30,
        tzinfo=timezone.utc,
    )


def test_winning_trade_calculation() -> None:
    entry_time = make_entry_time()
    exit_time = entry_time + timedelta(hours=2)

    result = TradeAnalytics.calculate(
        entry_price=200.0,
        stop_price=195.0,
        exit_price=210.0,
        quantity=10.0,
        entry_time=entry_time,
        exit_time=exit_time,
    )

    assert isinstance(result, TradeResult)
    assert result.realized_pl == pytest.approx(
        100.0
    )
    assert result.r_multiple == pytest.approx(
        2.0
    )
    assert (
        result.holding_duration_seconds
        == pytest.approx(7200.0)
    )


def test_losing_trade_calculation() -> None:
    entry_time = make_entry_time()
    exit_time = entry_time + timedelta(minutes=30)

    result = TradeAnalytics.calculate(
        entry_price=200.0,
        stop_price=195.0,
        exit_price=195.0,
        quantity=10.0,
        entry_time=entry_time,
        exit_time=exit_time,
    )

    assert result.realized_pl == pytest.approx(
        -50.0
    )
    assert result.r_multiple == pytest.approx(
        -1.0
    )
    assert (
        result.holding_duration_seconds
        == pytest.approx(1800.0)
    )


def test_break_even_trade_calculation() -> None:
    entry_time = make_entry_time()

    result = TradeAnalytics.calculate(
        entry_price=200.0,
        stop_price=195.0,
        exit_price=200.0,
        quantity=10.0,
        entry_time=entry_time,
        exit_time=entry_time,
    )

    assert result.realized_pl == pytest.approx(
        0.0
    )
    assert result.r_multiple == pytest.approx(
        0.0
    )
    assert (
        result.holding_duration_seconds
        == pytest.approx(0.0)
    )


def test_supplied_total_risk_is_used() -> None:
    entry_time = make_entry_time()

    result = TradeAnalytics.calculate(
        entry_price=200.0,
        stop_price=195.0,
        exit_price=210.0,
        quantity=10.0,
        entry_time=entry_time,
        exit_time=entry_time + timedelta(hours=1),
        total_risk=40.0,
    )

    assert result.realized_pl == pytest.approx(
        100.0
    )
    assert result.r_multiple == pytest.approx(
        2.5
    )


@pytest.mark.parametrize(
    ("field_name", "field_value"),
    [
        ("entry_price", 0.0),
        ("entry_price", -1.0),
        ("stop_price", 0.0),
        ("exit_price", 0.0),
        ("quantity", 0.0),
        ("quantity", -5.0),
    ],
)
def test_positive_values_are_required(
    field_name: str,
    field_value: float,
) -> None:
    values = {
        "entry_price": 200.0,
        "stop_price": 195.0,
        "exit_price": 210.0,
        "quantity": 10.0,
    }

    values[field_name] = field_value

    with pytest.raises(
        ValueError,
        match=(
            f"{field_name} must be greater than zero"
        ),
    ):
        TradeAnalytics.calculate(
            **values,
            entry_time=make_entry_time(),
            exit_time=(
                make_entry_time()
                + timedelta(hours=1)
            ),
        )


@pytest.mark.parametrize(
    "field_value",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_non_finite_values_are_rejected(
    field_value: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="exit_price must be finite",
    ):
        TradeAnalytics.calculate(
            entry_price=200.0,
            stop_price=195.0,
            exit_price=field_value,
            quantity=10.0,
            entry_time=make_entry_time(),
            exit_time=(
                make_entry_time()
                + timedelta(hours=1)
            ),
        )


def test_stop_must_be_below_entry_for_long_trade() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "stop_price must be below entry_price"
        ),
    ):
        TradeAnalytics.calculate(
            entry_price=200.0,
            stop_price=200.0,
            exit_price=210.0,
            quantity=10.0,
            entry_time=make_entry_time(),
            exit_time=(
                make_entry_time()
                + timedelta(hours=1)
            ),
        )


def test_exit_time_cannot_precede_entry_time() -> None:
    entry_time = make_entry_time()

    with pytest.raises(
        ValueError,
        match=(
            "exit_time cannot be earlier than entry_time"
        ),
    ):
        TradeAnalytics.calculate(
            entry_price=200.0,
            stop_price=195.0,
            exit_price=210.0,
            quantity=10.0,
            entry_time=entry_time,
            exit_time=(
                entry_time
                - timedelta(seconds=1)
            ),
        )


def test_entry_time_must_be_timezone_aware() -> None:
    naive_entry_time = datetime(
        2026,
        7,
        20,
        14,
        30,
    )

    with pytest.raises(
        ValueError,
        match=(
            "entry_time must be timezone-aware"
        ),
    ):
        TradeAnalytics.calculate(
            entry_price=200.0,
            stop_price=195.0,
            exit_price=210.0,
            quantity=10.0,
            entry_time=naive_entry_time,
            exit_time=make_entry_time(),
        )


def test_exit_time_must_be_timezone_aware() -> None:
    naive_exit_time = datetime(
        2026,
        7,
        20,
        15,
        30,
    )

    with pytest.raises(
        ValueError,
        match=(
            "exit_time must be timezone-aware"
        ),
    ):
        TradeAnalytics.calculate(
            entry_price=200.0,
            stop_price=195.0,
            exit_price=210.0,
            quantity=10.0,
            entry_time=make_entry_time(),
            exit_time=naive_exit_time,
        )


def test_total_risk_must_be_positive() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "total_risk must be greater than zero"
        ),
    ):
        TradeAnalytics.calculate(
            entry_price=200.0,
            stop_price=195.0,
            exit_price=210.0,
            quantity=10.0,
            entry_time=make_entry_time(),
            exit_time=(
                make_entry_time()
                + timedelta(hours=1)
            ),
            total_risk=0.0,
        )