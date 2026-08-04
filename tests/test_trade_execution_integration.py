from dataclasses import replace
from unittest.mock import MagicMock

from application.trade_workflow import TradeWorkflow
from execution.trade_executor import TradeExecutor
from models.preflight_result import PreflightResult
from models.trade import Trade, TradeStatus
from models.trade_signal import TradeSignal


def create_signal() -> TradeSignal:
    return TradeSignal(
        symbol="NVDA",
        signal_type="BUY",
        price=100.00,
        reason="Qualified integration-test signal",
        rsi=55.00,
        short_sma=101.00,
        long_sma=99.00,
    )


def test_approved_trade_flows_to_broker_and_repository() -> None:
    broker = MagicMock()
    journal = MagicMock()
    repository = MagicMock()

    submitted_order = MagicMock()
    submitted_order.id = "ORDER-123"

    broker.submit_bracket_order.return_value = (
        submitted_order
    )

    executor = TradeExecutor(
        broker=broker,
        journal=journal,
        repository=repository,
    )

    workflow = TradeWorkflow(
        account_equity=100_000.00,
        risk_percent=0.01,
        max_position_percent=0.10,
        stop_loss_percent=0.02,
        preflight_runner=lambda plan: PreflightResult(
            approved=True,
            reasons=[],
        ),
    )

    result = workflow.prepare_trade(
        create_signal()
    )

    result = replace(
        result,
        trade_id="trade-123",
    )

    assert result.ready_for_approval is True

    returned_order = executor.execute(
        result
    )

    assert returned_order is submitted_order

    broker.submit_bracket_order.assert_called_once_with(
        result.plan
    )

    repository.save.assert_called_once()

    saved_trade = repository.save.call_args.args[0]

    assert isinstance(saved_trade, Trade)
    assert saved_trade.trade_id == "trade-123"
    assert saved_trade.symbol == "NVDA"
    assert saved_trade.status is TradeStatus.SUBMITTED
    assert saved_trade.parent_order_id == "ORDER-123"

    journal.record_event.assert_called_once_with(
        symbol="NVDA",
        asset_type="stock",
        signal_type="BUY",
        entry_price=result.plan.entry_price,
        stop_price=result.plan.stop_price,
        target_price=result.plan.target_price,
        quantity=result.plan.quantity,
        total_risk=result.plan.total_risk,
        risk_reward_ratio=(
            result.plan.risk_reward_ratio
        ),
        status="trade_submitted",
        reason="Bracket order submitted to broker",
        trade_id="trade-123",
        order_id="ORDER-123",
    )