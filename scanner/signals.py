import pandas as pd

from models.trade_signal import TradeSignal


def check_sma_crossover(
    symbol: str,
    data: pd.DataFrame,
    short_period: int = 20,
    long_period: int = 50,
    rsi_period: int = 14,
    atr_period: int = 14,
    rsi_buy_max: float = 70.0,
    rsi_sell_min: float = 30.0,
) -> TradeSignal | None:
    """
    Detect an SMA crossover and confirm it with RSI.

    If an ATR column is present, the current ATR value is copied
    into the returned TradeSignal.
    """
    short_sma_column = f"SMA_{short_period}"
    long_sma_column = f"SMA_{long_period}"
    rsi_column = f"RSI_{rsi_period}"
    atr_column = f"ATR_{atr_period}"

    required_columns = {
        "Close",
        short_sma_column,
        long_sma_column,
        rsi_column,
    }

    missing_columns = required_columns.difference(data.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {missing}")

    valid_data = data.dropna(
        subset=[
            "Close",
            short_sma_column,
            long_sma_column,
            rsi_column,
        ]
    )

    if len(valid_data) < 2:
        return None

    previous_row = valid_data.iloc[-2]
    current_row = valid_data.iloc[-1]

    previous_short_sma = float(
        previous_row[short_sma_column]
    )
    previous_long_sma = float(
        previous_row[long_sma_column]
    )

    current_short_sma = float(
        current_row[short_sma_column]
    )
    current_long_sma = float(
        current_row[long_sma_column]
    )

    current_price = float(current_row["Close"])
    current_rsi = float(current_row[rsi_column])

    current_atr: float | None = None

    if (
        atr_column in current_row.index
        and pd.notna(current_row[atr_column])
    ):
        current_atr = float(current_row[atr_column])

    bullish_crossover = (
        previous_short_sma <= previous_long_sma
        and current_short_sma > current_long_sma
    )

    bearish_crossover = (
        previous_short_sma >= previous_long_sma
        and current_short_sma < current_long_sma
    )

    if bullish_crossover and current_rsi < rsi_buy_max:
        return TradeSignal(
            symbol=symbol,
            signal_type="BUY",
            price=current_price,
            reason=(
                "Bullish SMA crossover confirmed by "
                f"RSI {current_rsi:.2f}"
            ),
            rsi=current_rsi,
            short_sma=current_short_sma,
            long_sma=current_long_sma,
            atr=current_atr,
        )

    if bearish_crossover and current_rsi > rsi_sell_min:
        return TradeSignal(
            symbol=symbol,
            signal_type="SELL",
            price=current_price,
            reason=(
                "Bearish SMA crossover confirmed by "
                f"RSI {current_rsi:.2f}"
            ),
            rsi=current_rsi,
            short_sma=current_short_sma,
            long_sma=current_long_sma,
            atr=current_atr,
        )

    return None