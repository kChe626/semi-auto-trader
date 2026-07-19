from dataclasses import dataclass


@dataclass
class TradePlan:
    symbol: str
    signal_type: str
    entry_price: float
    stop_price: float
    target_price: float
    quantity: int
    risk_per_share: float
    reward_per_share: float
    total_risk: float
    risk_reward_ratio: float