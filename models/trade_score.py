from dataclasses import dataclass

from models.trade_plan import TradePlan


@dataclass(frozen=True)
class TradeScore:
    plan: TradePlan
    score: float
    reasons: list[str]