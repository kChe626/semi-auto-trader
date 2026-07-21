from pathlib import Path
from types import SimpleNamespace

import pytest

from database.trade_journal import TradeJournal


@pytest.fixture
def journal(
    tmp_path: Path,
) -> TradeJournal:
    return TradeJournal(
        tmp_path / "test_trade_journal.db"
    )


def test_record_event(
    journal: TradeJournal,
) -> None:
    event_id = journal.record_event(
        symbol="AAPL",
        status="signal_found",
        score=88.5,
        reason="Test signal",
    )

    assert event_id == 1

    events = journal.get_recent_events()

    assert len(events) == 1
    assert events[0]["symbol"] == "AAPL"
    assert events[0]["status"] == "signal_found"
    assert events[0]["score"] == 88.5
    assert events[0]["reason"] == "Test signal"


def test_record_plan(
    journal: TradeJournal,
) -> None:
    plan = SimpleNamespace(
        symbol="NVDA",
        signal_type="BUY",
        entry_price=150.0,
        stop_price=145.0,
        target_price=160.0,
        quantity=10,
        total_risk=50.0,
        risk_reward_ratio=2.0,
    )

    event_id = journal.record_plan(
        plan=plan,
        status="preflight_passed",
        score=91.25,
    )

    assert event_id == 1

    event = journal.get_recent_events()[0]

    assert event["symbol"] == "NVDA"
    assert event["signal_type"] == "BUY"
    assert event["entry_price"] == 150.0
    assert event["stop_price"] == 145.0
    assert event["target_price"] == 160.0
    assert event["quantity"] == 10
    assert event["total_risk"] == 50.0
    assert event["risk_reward_ratio"] == 2.0
    assert event["status"] == "preflight_passed"


def test_recent_events_returns_newest_first(
    journal: TradeJournal,
) -> None:
    journal.record_event(
        symbol="AAPL",
        status="first",
    )

    journal.record_event(
        symbol="MSFT",
        status="second",
    )

    events = journal.get_recent_events()

    assert events[0]["symbol"] == "MSFT"
    assert events[1]["symbol"] == "AAPL"


def test_recent_events_respects_limit(
    journal: TradeJournal,
) -> None:
    journal.record_event(
        symbol="AAPL",
        status="first",
    )

    journal.record_event(
        symbol="MSFT",
        status="second",
    )

    events = journal.get_recent_events(
        limit=1
    )

    assert len(events) == 1
    assert events[0]["symbol"] == "MSFT"


def test_recent_events_rejects_invalid_limit(
    journal: TradeJournal,
) -> None:
    with pytest.raises(
        ValueError,
        match="limit must be greater than zero",
    ):
        journal.get_recent_events(
            limit=0
        )