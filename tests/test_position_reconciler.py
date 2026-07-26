from pathlib import Path

from database.trade_journal import TradeJournal
from models.broker_state import PositionSnapshot
from trade_management.position_reconciler import (
    PositionReconciler,
)


def make_position() -> PositionSnapshot:
    return PositionSnapshot(
        symbol="AAPL",
        quantity=10,
        side="long",
        average_entry_price=200,
        current_price=205,
        market_value=2050,
        unrealized_profit_loss=50,
    )


def make_journal(
    tmp_path: Path,
) -> TradeJournal:
    return TradeJournal(
        tmp_path / "journal.db"
    )


def seed_tracked_trade(
    journal: TradeJournal,
) -> None:
    journal.record_event(
        symbol="AAPL",
        status="submitted_verified",
        signal_type="BUY",
        score=85.0,
        entry_price=200.0,
        stop_price=195.0,
        target_price=210.0,
        quantity=10.0,
        total_risk=50.0,
        risk_reward_ratio=2.0,
        reason="Order verified",
        trade_id="trade-1",
        order_id="order-1",
    )


def test_position_is_recorded(
    tmp_path: Path,
) -> None:
    journal = make_journal(tmp_path)
    seed_tracked_trade(journal)

    reconciler = PositionReconciler(
        journal
    )

    created = reconciler.reconcile_position(
        make_position()
    )

    assert created is True

    latest = (
        journal.get_latest_event_by_trade_id(
            "trade-1"
        )
    )

    assert latest is not None
    assert latest["status"] == "position_open"
    assert latest["trade_id"] == "trade-1"
    assert latest["order_id"] == "order-1"
    assert latest["symbol"] == "AAPL"
    assert latest["quantity"] == 10
    assert latest["entry_price"] == 200


def test_duplicate_position_not_recorded(
    tmp_path: Path,
) -> None:
    journal = make_journal(tmp_path)
    seed_tracked_trade(journal)

    reconciler = PositionReconciler(
        journal
    )

    first_created = reconciler.reconcile_position(
        make_position()
    )

    second_created = reconciler.reconcile_position(
        make_position()
    )

    assert first_created is True
    assert second_created is False

    events = journal.get_events_by_trade_id(
        "trade-1"
    )

    position_open_events = [
        event
        for event in events
        if event["status"] == "position_open"
    ]

    assert len(position_open_events) == 1


def test_untracked_broker_position_is_ignored(
    tmp_path: Path,
) -> None:
    journal = make_journal(tmp_path)

    reconciler = PositionReconciler(
        journal
    )

    created = reconciler.reconcile_position(
        make_position()
    )

    assert created is False
    assert journal.get_recent_events() == []


def test_closed_trade_is_not_reopened(
    tmp_path: Path,
) -> None:
    journal = make_journal(tmp_path)

    journal.record_event(
        symbol="AAPL",
        status="position_closed",
        trade_id="trade-1",
        order_id="order-1",
    )

    reconciler = PositionReconciler(
        journal
    )

    created = reconciler.reconcile_position(
        make_position()
    )

    assert created is False

    events = journal.get_events_by_trade_id(
        "trade-1"
    )

    assert len(events) == 1
    assert events[0]["status"] == "position_closed"