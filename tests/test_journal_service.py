from types import SimpleNamespace
from unittest.mock import Mock

from database.journal_service import (
    record_event_safely,
    record_plan_safely,
)


def test_record_event_safely_calls_journal() -> None:
    journal = Mock()
    journal.record_event.return_value = 12

    result = record_event_safely(
        journal,
        symbol="AAPL",
        status="signal_found",
        score=88.5,
        reason="Valid setup",
    )

    assert result == 12

    journal.record_event.assert_called_once_with(
        symbol="AAPL",
        status="signal_found",
        asset_type="stock",
        signal_type=None,
        score=88.5,
        entry_price=None,
        stop_price=None,
        target_price=None,
        quantity=None,
        total_risk=None,
        risk_reward_ratio=None,
        reason="Valid setup",
        trade_id=None,
        order_id=None,
    )


def test_record_event_safely_accepts_none() -> None:
    result = record_event_safely(
        None,
        symbol="AAPL",
        status="signal_found",
    )

    assert result is None


def test_record_event_safely_handles_failure(
    capsys,
) -> None:
    journal = Mock()

    journal.record_event.side_effect = RuntimeError(
        "database unavailable"
    )

    result = record_event_safely(
        journal,
        symbol="AAPL",
        status="signal_found",
    )

    assert result is None

    output = capsys.readouterr().out

    assert (
        "unable to record journal event"
        in output
    )
    assert "AAPL" in output
    assert "database unavailable" in output


def test_record_event_safely_forwards_trade_id() -> None:
    journal = Mock()
    journal.record_event.return_value = 13

    result = record_event_safely(
        journal,
        symbol="AAPL",
        status="submitted_verified",
        trade_id="trade-123",
        order_id="order-456",
    )

    assert result == 13

    journal.record_event.assert_called_once_with(
        symbol="AAPL",
        status="submitted_verified",
        asset_type="stock",
        signal_type=None,
        score=None,
        entry_price=None,
        stop_price=None,
        target_price=None,
        quantity=None,
        total_risk=None,
        risk_reward_ratio=None,
        reason=None,
        trade_id="trade-123",
        order_id="order-456",
    )


def test_record_plan_safely_calls_journal() -> None:
    journal = Mock()

    plan = SimpleNamespace(
        symbol="NVDA",
    )

    journal.record_plan.return_value = 25

    result = record_plan_safely(
        journal,
        plan=plan,
        status="preflight_passed",
        score=92.0,
        reason="All checks passed",
    )

    assert result == 25

    journal.record_plan.assert_called_once_with(
        plan=plan,
        status="preflight_passed",
        score=92.0,
        reason="All checks passed",
        trade_id=None,
        order_id=None,
        asset_type="stock",
    )


def test_record_plan_safely_accepts_none() -> None:
    plan = SimpleNamespace(
        symbol="NVDA",
    )

    result = record_plan_safely(
        None,
        plan=plan,
        status="candidate_ranked",
    )

    assert result is None


def test_record_plan_safely_handles_failure(
    capsys,
) -> None:
    journal = Mock()

    journal.record_plan.side_effect = RuntimeError(
        "write failed"
    )

    plan = SimpleNamespace(
        symbol="MSFT",
    )

    result = record_plan_safely(
        journal,
        plan=plan,
        status="candidate_ranked",
    )

    assert result is None

    output = capsys.readouterr().out

    assert (
        "unable to record trade plan"
        in output
    )
    assert "MSFT" in output
    assert "write failed" in output


def test_record_plan_safely_forwards_trade_id() -> None:
    journal = Mock()

    plan = SimpleNamespace(
        symbol="NVDA",
    )

    journal.record_plan.return_value = 26

    result = record_plan_safely(
        journal,
        plan=plan,
        status="submitted_verified",
        score=95.0,
        trade_id="trade-789",
        order_id="order-987",
    )

    assert result == 26

    journal.record_plan.assert_called_once_with(
        plan=plan,
        status="submitted_verified",
        score=95.0,
        reason=None,
        trade_id="trade-789",
        order_id="order-987",
        asset_type="stock",
    )