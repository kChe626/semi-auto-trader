import pandas as pd

from models.trade_signal import TradeSignal


def check_sma_crossover(
    symbol: str,
    bars: pd.DataFrame,
) -> TradeSignal | None:

    required_columns = {"Close", "SMA_20"}

    if not required_columns.issubset(bars.columns):
        raise ValueError(
            "DataFrame must contain Close and SMA_20 columns."
        )

    clean_bars = bars.dropna(subset=["Close", "SMA_20"])

    if len(clean_bars) < 2:
        return None

    previous = clean_bars.iloc[-2]
    latest = clean_bars.iloc[-1]

    crossed_above = (
        previous["Close"] <= previous["SMA_20"]
        and latest["Close"] > latest["SMA_20"]
    )

    if crossed_above:
        return TradeSignal(
            symbol=symbol,
            signal="BUY",
            price=float(latest["Close"]),
            sma20=float(latest["SMA_20"]),
        )

    return None