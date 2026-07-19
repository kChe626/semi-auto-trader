import pandas as pd


def add_sma(
    bars: pd.DataFrame,
    period: int = 20,
) -> pd.DataFrame:
    bars[f"SMA_{period}"] = (
        bars["Close"]
        .rolling(window=period)
        .mean()
    )

    return bars