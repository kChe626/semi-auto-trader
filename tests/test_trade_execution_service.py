from unittest.mock import Mock

from application.trade_execution_service import (
    TradeExecutionService,
)


def test_approved_trade_executes() -> None:
    approval = Mock(
        return_value=True
    )

    executor = Mock(
        return_value="ORDER-123"
    )

    service = TradeExecutionService(
        trade_approval=approval,
        trade_executor=executor,
    )

    workflow = Mock()

    result = service.execute(
        workflow
    )

    assert result == "ORDER-123"

    approval.assert_called_once_with(
        workflow.plan
    )

    executor.assert_called_once_with(
        workflow
    )


def test_rejected_trade_does_not_execute() -> None:
    approval = Mock(
        return_value=False
    )

    executor = Mock()

    service = TradeExecutionService(
        trade_approval=approval,
        trade_executor=executor,
    )

    workflow = Mock()

    result = service.execute(
        workflow
    )

    assert result is None

    approval.assert_called_once_with(
        workflow.plan
    )

    executor.assert_not_called()