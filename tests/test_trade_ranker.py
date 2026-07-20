from types import SimpleNamespace

from scanner.trade_ranker import (
    rank_trade_plans,
    select_best_trade,
)


def test_rank_trade_plans_highest_score_first(
    monkeypatch,
) -> None:
    plans = [
        SimpleNamespace(symbol="AAPL"),
        SimpleNamespace(symbol="NVDA"),
        SimpleNamespace(symbol="MSFT"),
    ]

    scores = {
        "AAPL": 70.0,
        "NVDA": 95.0,
        "MSFT": 82.0,
    }

    def fake_score_trade(plan):
        return SimpleNamespace(
            plan=plan,
            score=scores[plan.symbol],
            reasons=[],
        )

    monkeypatch.setattr(
        "scanner.trade_ranker.score_trade",
        fake_score_trade,
    )

    ranked = rank_trade_plans(plans)

    assert [
        result.plan.symbol
        for result in ranked
    ] == [
        "NVDA",
        "MSFT",
        "AAPL",
    ]


def test_rank_trade_plans_empty_list() -> None:
    assert rank_trade_plans([]) == []


def test_select_best_trade_returns_top_trade(
    monkeypatch,
) -> None:
    plans = [
        SimpleNamespace(symbol="META"),
        SimpleNamespace(symbol="AMZN"),
    ]

    def fake_score_trade(plan):
        scores = {
            "META": 80.0,
            "AMZN": 90.0,
        }

        return SimpleNamespace(
            plan=plan,
            score=scores[plan.symbol],
            reasons=[],
        )

    monkeypatch.setattr(
        "scanner.trade_ranker.score_trade",
        fake_score_trade,
    )

    best_trade = select_best_trade(plans)

    assert best_trade is not None
    assert best_trade.plan.symbol == "AMZN"
    assert best_trade.score == 90.0


def test_select_best_trade_returns_none_when_empty() -> None:
    assert select_best_trade([]) is None