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


def test_larger_bullish_sma_separation_scores_better() -> None:
    weak_trend = score_trade(
        make_plan(
            short_sma=100.5,
            long_sma=100.0,
        )
    )

    strong_trend = score_trade(
        make_plan(
            short_sma=102.0,
            long_sma=100.0,
        )
    )

    assert strong_trend.score > weak_trend.score


def test_larger_bearish_sma_separation_scores_better() -> None:
    weak_trend = score_trade(
        make_plan(
            signal_type="SELL",
            short_sma=99.5,
            long_sma=100.0,
        )
    )

    strong_trend = score_trade(
        make_plan(
            signal_type="SELL",
            short_sma=98.0,
            long_sma=100.0,
        )
    )

    assert strong_trend.score > weak_trend.score


def test_missing_indicator_values_are_allowed() -> None:
    result = score_trade(
        make_plan(
            rsi=None,
            short_sma=None,
            long_sma=None,
        )
    )

    assert result.score == pytest.approx(38.0)


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