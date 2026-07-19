from dataclasses import dataclass


@dataclass
class TradeSignal:
    symbol: str
    signal: str
    price: float
    sma20: float