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

def test_approved_trade_verifies_submitted_order() -> None:
    approval = Mock(
        return_value=True
    )

    executor = Mock(
        return_value="ORDER-123"
    )

    verifier = Mock(
        return_value="VERIFIED-ORDER-123"
    )

    service = TradeExecutionService(
        trade_approval=approval,
        trade_executor=executor,
        order_verifier=verifier,
    )

    workflow = Mock()

    result = service.execute(
        workflow
    )

    assert result == "VERIFIED-ORDER-123"

    executor.assert_called_once_with(
        workflow
    )

    verifier.assert_called_once_with(
        "ORDER-123"
    )