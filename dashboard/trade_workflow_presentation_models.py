from dataclasses import dataclass


@dataclass(frozen=True)
class TradeWorkflowViewModel:
    symbol: str
    side: str
    score: str
    minimum_score: str
    entry_price: str
    stop_price: str
    target_price: str
    quantity: str
    total_risk: str
    risk_reward_ratio: str
    status: str
    rejection_reasons: tuple[str, ...]