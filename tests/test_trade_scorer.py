from scanner.trade_scorer import score_trade
from models.trade_plan import TradePlan


def make_plan(rr, risk):
    return TradePlan(
        symbol="META",
        signal_type="BUY",
        entry_price=100,
        stop_price=98,
        target_price=104,
        quantity=10,
        risk_per_share=2,
        reward_per_share=4,
        total_risk=risk,
        risk_reward_ratio=rr,
    )


def test_higher_rr_scores_better():
    low = score_trade(make_plan(2.0, 200))
    high = score_trade(make_plan(3.0, 200))

    assert high.score > low.score


def test_lower_risk_scores_better():
    high_risk = score_trade(make_plan(2.5, 300))
    low_risk = score_trade(make_plan(2.5, 100))

    assert low_risk.score > high_risk.score