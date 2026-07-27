from unittest.mock import Mock

import pytest

from execution.trade_executor import TradeExecutor


def test_execute_submits_and_saves_trade() -> None:
    broker = Mock()
    journal = Mock()
    repository = Mock()

    workflow = Mock()
    workflow.status = "READY FOR APPROVAL"
    workflow.trade_id = "trade-123"

    submitted_order = Mock()
    broker.submit_order.return_value = submitted_order

    executor = TradeExecutor(
        broker=broker,
        journal=journal,
        repository=repository,
    )

    result = executor.execute(workflow)

    assert result is submitted_order

    broker.submit_order.assert_called_once_with(
        workflow
    )

    repository.save.assert_called_once_with(
        workflow
    )

    journal.record_event.assert_called_once_with(
        trade_id="trade-123",
        event="TRADE_SUBMITTED",
    )


def test_execute_rejects_workflow_not_ready() -> None:
    broker = Mock()
    journal = Mock()
    repository = Mock()

    workflow = Mock()
    workflow.status = "REJECTED"

    executor = TradeExecutor(
        broker=broker,
        journal=journal,
        repository=repository,
    )

    with pytest.raises(
        ValueError,
        match="Trade workflow is not ready for execution",
    ):
        executor.execute(workflow)

    broker.submit_order.assert_not_called()
    repository.save.assert_not_called()
    journal.record_event.assert_not_called()