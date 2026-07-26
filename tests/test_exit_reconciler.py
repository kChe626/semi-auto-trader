from datetime import datetime, timedelta
from pathlib import Path

import pytest

from database.trade_journal import TradeJournal
from models.broker_state import PositionSnapshot
from models.exit_fill import ExitFill
from trade_management.exit_reconciler import (
    ExitReconciler,
)


def make_journal(
    tmp_path: Path,
) -> TradeJournal:
    return TradeJournal(
        tmp_path / "journal.db"
    )


def make_position(
    symbol: str = "AAPL",
) -> PositionSnapshot:
    return PositionSnapshot(
        symbol=symbol,
        quantity=10,
        side="long",
        average_entry_price=200,
        current_price=205,
        market_value=2050,
        unrealized_profit_loss=50,
    )


def seed_open_trade(
    journal: TradeJournal,
    *,
    symbol: str = "AAPL",
    trade_id: str = "trade-1",
    order_id: str | None = "order-1",
) -> None:
    journal.record_event(
        symbol=symbol,
        status="position_open",
        signal_type="BUY",
        score=85.0,
        entry_price=200.0,
        stop_price=195.0,
        target_price=210.0,
        quantity=10.0,
        total_risk=50.0,
        risk_reward_ratio=2.0,
        reason="Broker position detected",
        trade_id=trade_id,
        order_id=order_id,
    )


class FakeExitLookup:
    def __init__(
        self,
        exit_fill: ExitFill | None,
    ) -> None:
        self.exit_fill = exit_fill
        self.requested_order_ids: list[str] = []

    def get_completed_exit(
        self,
        order_id: str,
    ) -> ExitFill | None:
        self.requested_order_ids.append(
            order_id
        )

        return self.exit_fill


def test_missing_position_is_closed(
    tmp_path: Path,
) -> None:
    journal = make_journal(tmp_path)
    seed_open_trade(journal)

    reconciler = ExitReconciler(
        journal
    )

    closed_count = (
        reconciler.reconcile_closed_positions(
            []
        )
    )

    assert closed_count == 1

    latest = (
        journal.get_latest_event_by_trade_id(
            "trade-1"
        )
    )

    assert latest is not None
    assert latest["status"] == "position_closed"
    assert latest["symbol"] == "AAPL"
    assert latest["trade_id"] == "trade-1"
    assert latest["order_id"] == "order-1"


def test_open_position_is_not_closed(
    tmp_path: Path,
) -> None:
    journal = make_journal(tmp_path)
    seed_open_trade(journal)

    reconciler = ExitReconciler(
        journal
    )

    closed_count = (
        reconciler.reconcile_closed_positions(
            [make_position()]
        )
    )

    assert closed_count == 0

    latest = (
        journal.get_latest_event_by_trade_id(
            "trade-1"
        )
    )

    assert latest is not None
    assert latest["status"] == "position_open"


def test_symbol_comparison_is_case_insensitive(
    tmp_path: Path,
) -> None:
    journal = make_journal(tmp_path)

    seed_open_trade(
        journal,
        symbol="aapl",
    )

    reconciler = ExitReconciler(
        journal
    )

    closed_count = (
        reconciler.reconcile_closed_positions(
            [make_position("AAPL")]
        )
    )

    assert closed_count == 0


def test_closed_trade_is_not_closed_twice(
    tmp_path: Path,
) -> None:
    journal = make_journal(tmp_path)
    seed_open_trade(journal)

    reconciler = ExitReconciler(
        journal
    )

    first_count = (
        reconciler.reconcile_closed_positions(
            []
        )
    )

    second_count = (
        reconciler.reconcile_closed_positions(
            []
        )
    )

    assert first_count == 1
    assert second_count == 0

    events = journal.get_events_by_trade_id(
        "trade-1"
    )

    closed_events = [
        event
        for event in events
        if event["status"]
        == "position_closed"
    ]

    assert len(closed_events) == 1


def test_multiple_missing_positions_are_closed(
    tmp_path: Path,
) -> None:
    journal = make_journal(tmp_path)

    seed_open_trade(
        journal,
        symbol="AAPL",
        trade_id="trade-1",
        order_id="order-1",
    )

    seed_open_trade(
        journal,
        symbol="MSFT",
        trade_id="trade-2",
        order_id="order-2",
    )

    reconciler = ExitReconciler(
        journal
    )

    closed_count = (
        reconciler.reconcile_closed_positions(
            []
        )
    )

    assert closed_count == 2


def test_only_missing_position_is_closed(
    tmp_path: Path,
) -> None:
    journal = make_journal(tmp_path)

    seed_open_trade(
        journal,
        symbol="AAPL",
        trade_id="trade-1",
        order_id="order-1",
    )

    seed_open_trade(
        journal,
        symbol="MSFT",
        trade_id="trade-2",
        order_id="order-2",
    )

    reconciler = ExitReconciler(
        journal
    )

    closed_count = (
        reconciler.reconcile_closed_positions(
            [make_position("AAPL")]
        )
    )

    assert closed_count == 1

    aapl_latest = (
        journal.get_latest_event_by_trade_id(
            "trade-1"
        )
    )

    msft_latest = (
        journal.get_latest_event_by_trade_id(
            "trade-2"
        )
    )

    assert aapl_latest is not None
    assert msft_latest is not None

    assert (
        aapl_latest["status"]
        == "position_open"
    )

    assert (
        msft_latest["status"]
        == "position_closed"
    )


def test_no_tracked_open_trades_returns_zero(
    tmp_path: Path,
) -> None:
    journal = make_journal(tmp_path)

    reconciler = ExitReconciler(
        journal
    )

    closed_count = (
        reconciler.reconcile_closed_positions(
            []
        )
    )

    assert closed_count == 0
    assert journal.get_recent_events() == []


def test_confirmed_exit_records_analytics(
    tmp_path: Path,
) -> None:
    journal = make_journal(tmp_path)
    seed_open_trade(journal)

    open_event = (
        journal.get_latest_event_by_trade_id(
            "trade-1"
        )
    )

    assert open_event is not None

    entry_time = datetime.fromisoformat(
        open_event["created_at"]
    )

    exit_fill = ExitFill(
        order_id="exit-order-1",
        filled_price=210.0,
        filled_quantity=10.0,
        filled_at=(
            entry_time
            + timedelta(hours=2)
        ),
    )

    exit_lookup = FakeExitLookup(
        exit_fill
    )

    reconciler = ExitReconciler(
        journal,
        exit_lookup=exit_lookup,
    )

    closed_count = (
        reconciler.reconcile_closed_positions(
            []
        )
    )

    assert closed_count == 1

    assert (
        exit_lookup.requested_order_ids
        == ["order-1"]
    )

    latest = (
        journal.get_latest_event_by_trade_id(
            "trade-1"
        )
    )

    assert latest is not None
    assert latest["status"] == "position_closed"

    assert latest["exit_price"] == pytest.approx(
        210.0
    )

    assert latest["realized_pl"] == pytest.approx(
        100.0
    )

    assert latest["r_multiple"] == pytest.approx(
        2.0
    )

    assert (
        latest["holding_duration_seconds"]
        == pytest.approx(7200.0)
    )

    assert (
        latest["exited_at"]
        == exit_fill.filled_at.isoformat()
    )

    assert latest["order_id"] == "order-1"

    assert latest["reason"] is not None

    assert (
        "exit_order_id=exit-order-1"
        in latest["reason"]
    )


def test_losing_exit_records_negative_results(
    tmp_path: Path,
) -> None:
    journal = make_journal(tmp_path)
    seed_open_trade(journal)

    open_event = (
        journal.get_latest_event_by_trade_id(
            "trade-1"
        )
    )

    assert open_event is not None

    entry_time = datetime.fromisoformat(
        open_event["created_at"]
    )

    exit_fill = ExitFill(
        order_id="exit-order-1",
        filled_price=195.0,
        filled_quantity=10.0,
        filled_at=(
            entry_time
            + timedelta(minutes=30)
        ),
    )

    reconciler = ExitReconciler(
        journal,
        exit_lookup=FakeExitLookup(
            exit_fill
        ),
    )

    closed_count = (
        reconciler.reconcile_closed_positions(
            []
        )
    )

    assert closed_count == 1

    latest = (
        journal.get_latest_event_by_trade_id(
            "trade-1"
        )
    )

    assert latest is not None

    assert latest["realized_pl"] == pytest.approx(
        -50.0
    )

    assert latest["r_multiple"] == pytest.approx(
        -1.0
    )

    assert (
        latest["holding_duration_seconds"]
        == pytest.approx(1800.0)
    )


def test_missing_confirmed_exit_does_not_close_trade(
    tmp_path: Path,
) -> None:
    journal = make_journal(tmp_path)
    seed_open_trade(journal)

    exit_lookup = FakeExitLookup(None)

    reconciler = ExitReconciler(
        journal,
        exit_lookup=exit_lookup,
    )

    closed_count = (
        reconciler.reconcile_closed_positions(
            []
        )
    )

    assert closed_count == 0

    latest = (
        journal.get_latest_event_by_trade_id(
            "trade-1"
        )
    )

    assert latest is not None
    assert latest["status"] == "position_open"

    assert (
        exit_lookup.requested_order_ids
        == ["order-1"]
    )


def test_missing_parent_order_id_does_not_close_trade(
    tmp_path: Path,
) -> None:
    journal = make_journal(tmp_path)

    seed_open_trade(
        journal,
        order_id=None,
    )

    exit_lookup = FakeExitLookup(None)

    reconciler = ExitReconciler(
        journal,
        exit_lookup=exit_lookup,
    )

    closed_count = (
        reconciler.reconcile_closed_positions(
            []
        )
    )

    assert closed_count == 0
    assert exit_lookup.requested_order_ids == []

    latest = (
        journal.get_latest_event_by_trade_id(
            "trade-1"
        )
    )

    assert latest is not None
    assert latest["status"] == "position_open"