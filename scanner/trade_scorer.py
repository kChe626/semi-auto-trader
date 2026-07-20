from models.trade_plan import TradePlan
from models.trade_score import TradeScore


def score_trade(plan: TradePlan) -> TradeScore:
    """
    Score a trade plan using reward/risk, total dollar risk,
    RSI quality, and SMA trend strength.

    Higher scores are preferred.
    """
    score = 0.0
    reasons: list[str] = []

    # Reward/risk score
    reward_risk_points = plan.risk_reward_ratio * 20
    score += reward_risk_points

    reasons.append(
        f"Reward/Risk {plan.risk_reward_ratio:.2f} "
        f"(+{reward_risk_points:.2f})"
    )

    # Total risk penalty
    risk_penalty = plan.total_risk / 100
    score -= risk_penalty

    reasons.append(
        f"Total risk ${plan.total_risk:,.2f} "
        f"(-{risk_penalty:.2f})"
    )

    # RSI score
    if plan.rsi is not None:
        rsi_points = calculate_rsi_score(
            signal_type=plan.signal_type,
            rsi=plan.rsi,
        )
        score += rsi_points

        reasons.append(
            f"RSI {plan.rsi:.2f} "
            f"(+{rsi_points:.2f})"
        )

    # SMA trend-strength score
    if (
        plan.short_sma is not None
        and plan.long_sma is not None
        and plan.long_sma > 0
    ):
        sma_distance_percent = (
            plan.short_sma - plan.long_sma
        ) / plan.long_sma * 100

        if plan.signal_type.upper() == "SELL":
            sma_distance_percent *= -1

        sma_points = max(
            0.0,
            min(sma_distance_percent * 10, 20.0),
        )

        score += sma_points

        reasons.append(
            f"SMA separation "
            f"{sma_distance_percent:.2f}% "
            f"(+{sma_points:.2f})"
        )

    return TradeScore(
        plan=plan,
        score=score,
        reasons=reasons,
    )


def calculate_rsi_score(
    signal_type: str,
    rsi: float,
) -> float:
    """
    Score RSI quality from 0 to 20 points.

    BUY trades:
        RSI near 50 is preferred.
        Very high RSI receives fewer points.

    SELL trades:
        RSI near 50 is preferred.
        Very low RSI receives fewer points.
    """
    normalized_signal_type = signal_type.upper()

    if normalized_signal_type == "BUY":
        if rsi <= 50:
            return 20.0

        return max(
            0.0,
            20.0 - (rsi - 50.0),
        )

    if normalized_signal_type == "SELL":
        if rsi >= 50:
            return 20.0

        return max(
            0.0,
            20.0 - (50.0 - rsi),
        )

    return 0.0