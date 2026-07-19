from models.trade_signal import TradeSignal

from config.watchlist import WATCHLIST
from scanner.indicators import add_sma
from scanner.market_data import get_historical_bars
from scanner.signals import check_sma_crossover


def scan_market() -> list[TradeSignal]:
    buy_signals = []

    for symbol in WATCHLIST:
        bars = get_historical_bars(symbol)

        if bars.empty:
            print(f"{symbol:6} -> NO DATA")
            continue

        bars = add_sma(bars, period=20)

        signal = check_sma_crossover(symbol, bars)

        if signal:
            print(
                f"{signal.symbol:6}"
                f" BUY"
                f"  Price: ${signal.price:.2f}"
                f"  SMA20: ${signal.sma20:.2f}"
            )

            buy_signals.append(signal)

        else:
            print(f"{symbol:6} -> NO BUY")

    return buy_signals