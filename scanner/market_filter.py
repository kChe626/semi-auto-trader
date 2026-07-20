from scanner.indicators import add_sma
from scanner.market_data import get_historical_bars


MARKET_SYMBOL = "SPY"
MARKET_SMA_PERIOD = 50


def market_is_bullish() -> bool:
    """
    Return True when SPY closes above its 50-day SMA.
    """

    data = get_historical_bars(MARKET_SYMBOL)

    if data.empty:
        raise ValueError(
            f"No historical data returned for {MARKET_SYMBOL}."
        )

    data = add_sma(
        data,
        MARKET_SMA_PERIOD,
    )

    sma_column = f"SMA_{MARKET_SMA_PERIOD}"

    if sma_column not in data.columns:
        raise ValueError(
            f"Expected indicator column {sma_column} "
            "was not created."
        )

    latest = data.iloc[-1]

    close_price = latest["Close"]
    sma_value = latest[sma_column]

    if close_price != close_price or sma_value != sma_value:
        raise ValueError(
            "Latest SPY close or SMA value is missing."
        )

    return bool(close_price > sma_value)