from datetime import datetime, timezone

import pandas as pd
import pytest

from trade_management.position_management_metrics import (
    calculate_trading_days_held,
    get_latest_sma_values,
)


def make_market_data(
    dates: list[str],
    closes: list[float],
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Close": closes,
        },
        index=pd.to_datetime(
            dates
        ),
    )


def test_opening_session_is_day_zero() -> None:
    data = make_market_data(
        [
            "2026-08-10",
        ],
        [
            100.0,
        ],
    )

    opened_at = datetime(
        2026,
        8,
        10,
        17,
        0,
        tzinfo=timezone.utc,
    )

    assert (
        calculate_trading_days_held(
            data,
            opened_at=opened_at,
        )
        == 0
    )


def test_counts_market_sessions_after_open() -> None:
    data = make_market_data(
        [
            "2026-08-10",
            "2026-08-11",
            "2026-08-12",
            "2026-08-13",
        ],
        [
            100.0,
            101.0,
            102.0,
            103.0,
        ],
    )

    opened_at = datetime(
        2026,
        8,
        10,
        17,
        0,
        tzinfo=timezone.utc,
    )

    assert (
        calculate_trading_days_held(
            data,
            opened_at=opened_at,
        )
        == 3
    )


def test_weekend_is_not_counted() -> None:
    data = make_market_data(
        [
            "2026-08-14",
            "2026-08-17",
        ],
        [
            100.0,
            101.0,
        ],
    )

    opened_at = datetime(
        2026,
        8,
        14,
        17,
        0,
        tzinfo=timezone.utc,
    )

    assert (
        calculate_trading_days_held(
            data,
            opened_at=opened_at,
        )
        == 1
    )


def test_empty_data_returns_zero_days() -> None:
    data = pd.DataFrame()

    opened_at = datetime(
        2026,
        8,
        10,
        tzinfo=timezone.utc,
    )

    assert (
        calculate_trading_days_held(
            data,
            opened_at=opened_at,
        )
        == 0
    )


def test_returns_latest_sma_values() -> None:
    closes = [
        float(value)
        for value in range(
            1,
            41,
        )
    ]

    dates = pd.date_range(
        "2026-06-01",
        periods=40,
        freq="B",
    )

    data = pd.DataFrame(
        {
            "Close": closes,
        },
        index=dates,
    )

    short_sma, long_sma = (
        get_latest_sma_values(
            data
        )
    )

    assert short_sma == pytest.approx(
        sum(closes[-10:]) / 10
    )

    assert long_sma == pytest.approx(
        sum(closes[-30:]) / 30
    )


def test_sma_calculation_requires_enough_data() -> None:
    data = make_market_data(
        [
            "2026-08-10",
            "2026-08-11",
        ],
        [
            100.0,
            101.0,
        ],
    )

    with pytest.raises(
        ValueError,
        match="not enough historical data",
    ):
        get_latest_sma_values(
            data
        )