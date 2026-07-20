from dataclasses import dataclass


@dataclass
class TradeSignal:
    symbol: str
    signal_type: str
    price: float
    reason: str
    rsi: float | None = None
    short_sma: float | None = None
    long_sma: float | None = None
    atr: float | None = None