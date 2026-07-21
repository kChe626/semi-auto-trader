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
        reason="Valid setup",
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

    assert "Trade journal write failed" in output
    assert "database unavailable" in output


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
        order_id=None,
        asset_type="stock",
    )


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

    assert "Trade journal write failed" in output
    assert "write failed" in output