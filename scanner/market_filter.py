from enum import Enum

from scanner.indicators import add_sma
from scanner.market_data import get_historical_bars


MARKET_SYMBOL = "SPY"
MARKET_SMA_PERIOD = 50
NEUTRAL_THRESHOLD = 0.01


class MarketRegime(str, Enum):
    BULLISH = "BULLISH"
    NEUTRAL = "NEUTRAL"
    BEARISH = "BEARISH"


def get_market_regime() -> MarketRegime:
    """
    Classify the broader market using SPY's latest close
    relative to its 50-day simple moving average.

    Bullish:
        More than 1% above SMA50.

    Neutral:
        Within 1% above or below SMA50.

    Bearish:
        More than 1% below SMA50.
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

    if sma_value <= 0:
        raise ValueError(
            "SPY SMA value must be greater than zero."
        )

    distance_from_sma = (
        close_price - sma_value
    ) / sma_value

    if distance_from_sma > NEUTRAL_THRESHOLD:
        return MarketRegime.BULLISH

    if distance_from_sma < -NEUTRAL_THRESHOLD:
        return MarketRegime.BEARISH

    return MarketRegime.NEUTRAL


def market_is_bullish() -> bool:
    """
    Backward-compatible helper.

    Neutral conditions are allowed because the market
    is not meaningfully below its 50-day SMA.
    """

    return get_market_regime() in {
        MarketRegime.BULLISH,
        MarketRegime.NEUTRAL,
    }