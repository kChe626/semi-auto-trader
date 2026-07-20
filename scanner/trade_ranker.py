from collections.abc import Iterable

from models.trade_plan import TradePlan
from models.trade_score import TradeScore
from scanner.trade_scorer import score_trade


def rank_trade_plans(
    plans: Iterable[TradePlan],
) -> list[TradeScore]:
    """
    Score trade plans and return them from highest
    score to lowest score.
    """

    scored_trades = [
        score_trade(plan)
        for plan in plans
    ]

    return sorted(
        scored_trades,
        key=lambda trade_score: trade_score.score,
        reverse=True,
    )


def select_best_trade(
    plans: Iterable[TradePlan],
) -> TradeScore | None:
    """
    Return the highest-scoring trade.

    Returns None when no plans are supplied.
    """

    ranked_trades = rank_trade_plans(plans)

    if not ranked_trades:
        return None

    return ranked_trades[0]