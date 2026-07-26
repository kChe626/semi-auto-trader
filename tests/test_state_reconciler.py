from pathlib import Path

from database.trade_journal import TradeJournal
from models.broker_state import OrderSnapshot
from trade_management.state_reconciler import (
    TradeStateReconciler,
)


def make_order(
    *,
    order_id: str = "order-123",
    symbol: str = "AAPL",
    status: str = "filled",
) -> OrderSnapshot:
    return OrderSnapshot(
        order_id=order_id,
        symbol=symbol,
        status=status,
        side="buy",
        quantity=5.0,
        filled_quantity=5.0,
        filled_average_price=200.0,
        order_class="bracket",
        submitted_at=None,
        filled_at=None,
        cancelled_at=None,
    )


def make_journal(
    tmp_path: Path,
) -> TradeJournal:
    return TradeJournal(
        tmp_path / "trade_journal.db"
    )


def test_reconcile_records_new_status(
    tmp_path: Path,
) -> None:
    journal = make_journal(tmp_path)

    journal.record_event(
        symbol="AAPL",
        status="submitted_verified",
        order_id="order-123",
    )

    reconciler = TradeStateReconciler(journal)

    result = reconciler.reconcile_order(
        make_order(status="filled")
    )

    assert result.order_id == "order-123"
    assert result.symbol == "AAPL"
    assert result.broker_status == "filled"
    assert (
        result.previous_status
        == "submitted_verified"
    )
    assert result.recorded_status == "order_filled"
    assert result.changed is True

    events = journal.get_events_by_order_id(
        "order-123"
    )

    assert len(events) == 2
    assert events[-1]["status"] == "order_filled"


def test_reconcile_does_not_duplicate_status(
    tmp_path: Path,
) -> None:
    journal = make_journal(tmp_path)

    journal.record_event(
        symbol="AAPL",
        status="order_filled",
        order_id="order-123",
    )

    reconciler = TradeStateReconciler(journal)

    result = reconciler.reconcile_order(
        make_order(status="filled")
    )

    assert result.previous_status == "order_filled"
    assert result.recorded_status == "order_filled"
    assert result.changed is False

    events = journal.get_events_by_order_id(
        "order-123"
    )

    assert len(events) == 1


def test_reconcile_handles_unknown_status(
    tmp_path: Path,
) -> None:
    journal = make_journal(tmp_path)
    reconciler = TradeStateReconciler(journal)

    result = reconciler.reconcile_order(
        make_order(status="mystery_status")
    )

    assert result.broker_status == "mystery_status"
    assert result.previous_status is None
    assert result.recorded_status is None
    assert result.changed is False

    events = journal.get_events_by_order_id(
        "order-123"
    )

    assert events == []


def test_reconcile_records_partially_filled(
    tmp_path: Path,
) -> None:
    journal = make_journal(tmp_path)
    reconciler = TradeStateReconciler(journal)

    order = make_order(
        status="partially_filled"
    )

    result = reconciler.reconcile_order(order)

    assert (
        result.recorded_status
        == "order_partially_filled"
    )
    assert result.changed is True

    latest = journal.get_latest_event_by_order_id(
        "order-123"
    )

    assert latest is not None
    assert (
        latest["status"]
        == "order_partially_filled"
    )


def test_reconcile_records_cancelled_status(
    tmp_path: Path,
) -> None:
    journal = make_journal(tmp_path)
    reconciler = TradeStateReconciler(journal)

    result = reconciler.reconcile_order(
        make_order(status="canceled")
    )

    assert (
        result.recorded_status
        == "order_cancelled"
    )
    assert result.changed is True


def test_reconcile_records_rejected_status(
    tmp_path: Path,
) -> None:
    journal = make_journal(tmp_path)
    reconciler = TradeStateReconciler(journal)

    result = reconciler.reconcile_order(
        make_order(status="rejected")
    )

    assert (
        result.recorded_status
        == "order_rejected"
    )
    assert result.changed is True


def test_reconcile_normalizes_broker_status_case(
    tmp_path: Path,
) -> None:
    journal = make_journal(tmp_path)
    reconciler = TradeStateReconciler(journal)

    result = reconciler.reconcile_order(
        make_order(status="FILLED")
    )

    assert result.recorded_status == "order_filled"
    assert result.changed is True