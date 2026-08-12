import pytest

from models.trade_plan import TradePlan
from scanner.trade_scorer import (
    calculate_rsi_score,
    score_trade,
)


def make_plan(
    rr: float = 2.0,
    risk: float = 200.0,
    signal_type: str = "BUY",
    rsi: float | None = None,
    short_sma: float | None = None,
    long_sma: float | None = None,
) -> TradePlan:
    return TradePlan(
        symbol="META",
        signal_type=signal_type,
        entry_price=100.0,
        stop_price=98.0,
        target_price=104.0,
        quantity=10,
        risk_per_share=2.0,
        reward_per_share=4.0,
        total_risk=risk,
        risk_reward_ratio=rr,
        rsi=rsi,
        short_sma=short_sma,
        long_sma=long_sma,
    )


def test_higher_rr_scores_better() -> None:
    low = score_trade(
        make_plan(
            rr=2.0,
            risk=200.0,
        )
    )

    high = score_trade(
        make_plan(
            rr=3.0,
            risk=200.0,
        )
    )

    assert high.score > low.score


def test_lower_risk_scores_better() -> None:
    high_risk = score_trade(
        make_plan(
            rr=2.5,
            risk=300.0,
        )
    )

    low_risk = score_trade(
        make_plan(
            rr=2.5,
            risk=100.0,
        )
    )

    assert low_risk.score > high_risk.score


def test_buy_rsi_near_fifty_scores_better() -> None:
    preferred = score_trade(
        make_plan(
            rsi=52.0,
        )
    )

    overbought = score_trade(
        make_plan(
            rsi=68.0,
        )
    )

    assert preferred.score > overbought.score


def test_sell_rsi_near_fifty_scores_better() -> None:
    preferred = score_trade(
        make_plan(
            signal_type="SELL",
            rsi=48.0,
        )
    )

    oversold = score_trade(
        make_plan(
            signal_type="SELL",
            rsi=32.0,
        )
    )

    assert preferred.score > oversold.score


def test_valid_bullish_crossover_gets_base_bonus() -> None:
    result = score_trade(
        make_plan(
            rsi=50.0,
            short_sma=100.01,
            long_sma=100.0,
        )
    )

    # Base score:
    # R/R 2.0 = +40
    # Risk $200 = -2
    # RSI 50 = +20
    # Fresh crossover = +10
    # SMA separation ~= +0.01
    assert result.score > 68.0

    assert any(
        "Fresh SMA crossover"
        in reason
        for reason in result.reasons
    )


def test_larger_bullish_sma_separation_scores_better() -> None:
    weak_trend = score_trade(
        make_plan(
            short_sma=100.1,
            long_sma=100.0,
        )
    )

    strong_trend = score_trade(
        make_plan(
            short_sma=101.0,
            long_sma=100.0,
        )
    )

    assert strong_trend.score > weak_trend.score


def test_larger_bearish_sma_separation_scores_better() -> None:
    weak_trend = score_trade(
        make_plan(
            signal_type="SELL",
            short_sma=99.9,
            long_sma=100.0,
        )
    )

    strong_trend = score_trade(
        make_plan(
            signal_type="SELL",
            short_sma=99.0,
            long_sma=100.0,
        )
    )

    assert strong_trend.score > weak_trend.score


def test_sma_separation_bonus_is_capped_at_ten() -> None:
    result = score_trade(
        make_plan(
            short_sma=110.0,
            long_sma=100.0,
        )
    )

    sma_reasons = [
        reason
        for reason in result.reasons
        if "SMA separation" in reason
    ]

    assert len(sma_reasons) == 1
    assert "(+10.00)" in sma_reasons[0]


def test_total_sma_contribution_is_capped_at_twenty() -> None:
    result = score_trade(
        make_plan(
            short_sma=110.0,
            long_sma=100.0,
        )
    )

    crossover_reason = next(
        reason
        for reason in result.reasons
        if "Fresh SMA crossover" in reason
    )

    separation_reason = next(
        reason
        for reason in result.reasons
        if "SMA separation" in reason
    )

    assert "(+10.00)" in crossover_reason
    assert "(+10.00)" in separation_reason


def test_missing_indicator_values_are_allowed() -> None:
    result = score_trade(
        make_plan(
            rsi=None,
            short_sma=None,
            long_sma=None,
        )
    )

    assert result.score == pytest.approx(
        38.0
    )


def test_rsi_score_never_goes_negative() -> None:
    assert (
        calculate_rsi_score(
            signal_type="BUY",
            rsi=90.0,
        )
        == 0.0
    )

    assert (
        calculate_rsi_score(
            signal_type="SELL",
            rsi=10.0,
        )
        == 0.0
    )