from unittest.mock import Mock

import pytest

from execution.trade_executor import TradeExecutor
from execution.trade_mapper import TradeMapper
from models.trade import Trade, TradeStatus
from models.trade_plan import TradePlan
from models.workflow_result import WorkflowResult


def _make_trade_plan() -> TradePlan:
    return TradePlan(
        symbol="AAPL",
        signal_type="BUY",
        entry_price=200.00,
        stop_price=195.00,
        target_price=210.00,
        quantity=10,
        risk_per_share=5.00,
        reward_per_share=10.00,
        total_risk=50.00,
        risk_reward_ratio=2.00,
    )


def _make_workflow(
    *,
    ready_for_approval: bool = True,
) -> WorkflowResult:
    return WorkflowResult(
        ready_for_approval=ready_for_approval,
        plan=_make_trade_plan(),
        preflight=Mock(),
    )


def test_execute_uses_current_workflow_and_persists_submitted_trade() -> None:
    workflow = _make_workflow()

    submitted_order = Mock()
    submitted_order.id = "parent-order-123"

    broker = Mock()
    broker.submit_bracket_order.return_value = (
        submitted_order
    )

    repository = Mock()
    journal = Mock()

    executor = TradeExecutor(
        broker=broker,
        repository=repository,
        journal=journal,
    )

    result = executor.execute(workflow)

    assert result is submitted_order

    broker.submit_bracket_order.assert_called_once_with(
        workflow.plan
    )
    repository.save.assert_called_once()
    journal.record_event.assert_called_once()

    saved_trade = repository.save.call_args.args[0]

    assert isinstance(saved_trade, Trade)
    assert saved_trade.symbol == "AAPL"
    assert saved_trade.quantity == 10
    assert saved_trade.status == TradeStatus.SUBMITTED
    assert saved_trade.entry_price == 200.00
    assert saved_trade.stop_price == 195.00
    assert saved_trade.target_price == 210.00
    assert (
        saved_trade.parent_order_id
        == "parent-order-123"
    )


def test_execute_rejects_workflow_not_ready_for_approval() -> None:
    workflow = _make_workflow(
        ready_for_approval=False,
    )

    broker = Mock()
    repository = Mock()
    journal = Mock()

    executor = TradeExecutor(
        broker=broker,
        repository=repository,
        journal=journal,
    )

    with pytest.raises(
        ValueError,
        match="Trade workflow is not ready for execution",
    ):
        executor.execute(workflow)

    broker.submit_bracket_order.assert_not_called()
    repository.save.assert_not_called()
    journal.record_event.assert_not_called()


def test_execute_rejects_submitted_order_without_id() -> None:
    workflow = _make_workflow()

    broker = Mock()
    broker.submit_bracket_order.return_value = object()

    repository = Mock()
    journal = Mock()

    executor = TradeExecutor(
        broker=broker,
        repository=repository,
        journal=journal,
    )

    with pytest.raises(
        ValueError,
        match="Submitted order is missing an id",
    ):
        executor.execute(workflow)

    broker.submit_bracket_order.assert_called_once_with(
        workflow.plan
    )
    repository.save.assert_not_called()
    journal.record_event.assert_not_called()


def test_execute_rejects_submitted_order_with_none_id() -> None:
    workflow = _make_workflow()

    submitted_order = Mock()
    submitted_order.id = None

    broker = Mock()
    broker.submit_bracket_order.return_value = (
        submitted_order
    )

    repository = Mock()
    journal = Mock()

    executor = TradeExecutor(
        broker=broker,
        repository=repository,
        journal=journal,
    )

    with pytest.raises(
        ValueError,
        match="Submitted order is missing an id",
    ):
        executor.execute(workflow)

    broker.submit_bracket_order.assert_called_once_with(
        workflow.plan
    )
    repository.save.assert_not_called()
    journal.record_event.assert_not_called()


def test_execute_uses_trade_mapper_to_build_submitted_trade(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workflow = _make_workflow()

    submitted_order = Mock()
    submitted_order.id = "parent-order-456"

    broker = Mock()
    broker.submit_bracket_order.return_value = (
        submitted_order
    )

    mapped_trade = Mock()
    mapped_trade.trade_id = "trade-456"

    map_submitted_trade = Mock(
        return_value=mapped_trade,
    )

    monkeypatch.setattr(
        TradeMapper,
        "map_submitted_trade",
        map_submitted_trade,
    )

    repository = Mock()
    journal = Mock()

    executor = TradeExecutor(
        broker=broker,
        repository=repository,
        journal=journal,
    )

    result = executor.execute(workflow)

    assert result is submitted_order

    map_submitted_trade.assert_called_once_with(
        plan=workflow.plan,
        parent_order_id="parent-order-456",
    )
    repository.save.assert_called_once_with(
        mapped_trade
    )
    journal.record_event.assert_called_once()


def test_execute_propagates_repository_failure() -> None:
    workflow = _make_workflow()

    submitted_order = Mock()
    submitted_order.id = "parent-order-789"

    broker = Mock()
    broker.submit_bracket_order.return_value = (
        submitted_order
    )

    repository = Mock()
    repository.save.side_effect = RuntimeError(
        "database unavailable"
    )

    journal = Mock()

    executor = TradeExecutor(
        broker=broker,
        repository=repository,
        journal=journal,
    )

    with pytest.raises(
        RuntimeError,
        match="database unavailable",
    ):
        executor.execute(workflow)

    broker.submit_bracket_order.assert_called_once_with(
        workflow.plan
    )
    repository.save.assert_called_once()
    journal.record_event.assert_not_called()