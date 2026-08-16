from __future__ import annotations

from datetime import datetime

import pandas as pd

from scanner.indicators import add_sma


def calculate_trading_days_held(
    data: pd.DataFrame,
    *,
    opened_at: datetime,
) -> int:
    """
    Count completed market sessions after the
    position's opening date.

    The opening session is day 0.

    Example:
        Open Monday -> Monday = 0
        Tuesday = 1
        Wednesday = 2
        Thursday = 3

    Because the calculation uses actual historical
    bars, weekends and exchange holidays are skipped.
    """

    if data.empty:
        return 0

    opened_date = opened_at.date()

    session_dates = {
        timestamp.date()
        for timestamp in pd.to_datetime(
            data.index
        )
        if timestamp.date() > opened_date
    }

    return len(session_dates)


def get_latest_sma_values(
    data: pd.DataFrame,
    *,
    short_period: int = 10,
    long_period: int = 30,
) -> tuple[float, float]:
    """
    Calculate and return the latest valid short and
    long simple moving averages.
    """

    if data.empty:
        raise ValueError(
            "historical data cannot be empty"
        )

    calculated = add_sma(
        data,
        period=short_period,
    )

    calculated = add_sma(
        calculated,
        period=long_period,
    )

    short_column = (
        f"SMA_{short_period}"
    )

    long_column = (
        f"SMA_{long_period}"
    )

    valid = calculated.dropna(
        subset=[
            short_column,
            long_column,
        ]
    )

    if valid.empty:
        raise ValueError(
            "not enough historical data "
            "to calculate moving averages"
        )

    latest = valid.iloc[-1]

    return (
        float(
            latest[
                short_column
            ]
        ),
        float(
            latest[
                long_column
            ]
        ),
    )