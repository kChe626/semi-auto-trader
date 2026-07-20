from models.trade_plan import TradePlan
from models.trade_score import TradeScore


def score_trade(plan: TradePlan) -> TradeScore:
    score = 0.0
    reasons: list[str] = []

    # Higher reward/risk gets more points
    score += plan.risk_reward_ratio * 20
    reasons.append(
        f"Reward/Risk {plan.risk_reward_ratio:.2f}"
    )

    # Smaller dollar risk is slightly preferred
    score -= plan.total_risk / 100

    return TradeScore(
        plan=plan,
        score=score,
        reasons=reasons,
    )