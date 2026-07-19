import pandas as pd


def add_sma(
    data: pd.DataFrame,
    period: int,
    price_column: str = "Close",
) -> pd.DataFrame:
    """
    Add a Simple Moving Average column to a market-data DataFrame.

    Example:
        add_sma(data, period=20)

    Creates:
        SMA_20
    """
    if period <= 0:
        raise ValueError("SMA period must be greater than zero.")

    if price_column not in data.columns:
        raise ValueError(f"Missing required column: {price_column}")

    result = data.copy()
    result[f"SMA_{period}"] = result[price_column].rolling(window=period).mean()

    return result


def add_rsi(
    data: pd.DataFrame,
    period: int = 14,
    price_column: str = "Close",
) -> pd.DataFrame:
    """
    Add a Relative Strength Index column to a market-data DataFrame.

    RSI measures the strength of recent price gains compared with
    recent price losses.

    Common interpretation:
        RSI above 70: potentially overbought
        RSI below 30: potentially oversold

    Creates:
        RSI_14 when period=14
    """
    if period <= 0:
        raise ValueError("RSI period must be greater than zero.")

    if price_column not in data.columns:
        raise ValueError(f"Missing required column: {price_column}")

    result = data.copy()

    price_change = result[price_column].diff()

    gains = price_change.clip(lower=0)
    losses = -price_change.clip(upper=0)

    average_gain = gains.ewm(
        alpha=1 / period,
        min_periods=period,
        adjust=False,
    ).mean()

    average_loss = losses.ewm(
        alpha=1 / period,
        min_periods=period,
        adjust=False,
    ).mean()

    relative_strength = average_gain / average_loss

    result[f"RSI_{period}"] = 100 - (
        100 / (1 + relative_strength)
    )

    return result