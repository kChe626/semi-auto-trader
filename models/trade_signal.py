from dataclasses import dataclass


@dataclass
class TradeSignal:
    symbol: str
    signal_type: str
    price: float
    reason: str