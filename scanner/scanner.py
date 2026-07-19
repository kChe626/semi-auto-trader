from models.trade_signal import TradeSignal

from config.watchlist import WATCHLIST
from scanner.indicators import add_rsi, add_sma
from scanner.market_data import get_historical_bars
from scanner.signals import check_sma_crossover


def scan_market() -> list[TradeSignal]:
    """
    Scan every symbol in the watchlist and return valid trade signals.
    """
    signals: list[TradeSignal] = []

    for symbol in WATCHLIST:
        bars = get_historical_bars(symbol)

        if bars.empty:
            print(f"{symbol:6} -> NO DATA")
            continue

        try:
            bars = add_sma(bars, period=20)
            bars = add_sma(bars, period=50)
            bars = add_rsi(bars, period=14)

            signal = check_sma_crossover(
                symbol=symbol,
                data=bars,
                short_period=20,
                long_period=50,
                rsi_period=14,
            )

        except (ValueError, KeyError) as error:
            print(f"{symbol:6} -> ERROR: {error}")
            continue

        if signal is None:
            print(f"{symbol:6} -> NO SIGNAL")
            continue

        print(
            f"{signal.symbol:6} -> {signal.signal_type}"
            f"  Price: ${signal.price:,.2f}"
            f"  Reason: {signal.reason}"
        )

        signals.append(signal)

    return signals