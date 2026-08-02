from unittest.mock import MagicMock

from application.trade_workflow import TradeWorkflow
from execution.trade_executor import TradeExecutor
from models.preflight_result import PreflightResult
from models.trade_signal import TradeSignal
from risk.signal_to_plan import create_trade_plan_from_signal


def create_signal() -> TradeSignal:
    return TradeSignal(
        symbol="NVDA",
        signal_type="BUY",
        price=100.00,
        reason="Bullish crossover",
        atr=2.00,
        rsi=55.00,
        short_sma=101.00,
        long_sma=99.00,
    )


def test_approved_trade_flows_to_broker_and_repository() -> None:
    broker = MagicMock()
    journal = MagicMock()
    repository = MagicMock()

    broker.submit_bracket_order.return_value = (
        MagicMock(id="ORDER-123")
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

    assert result.ready_for_approval is True

    executor.execute(
        result
    )

    broker.submit_bracket_order.assert_called_once()

    repository.save.assert_called_once()

    journal.record_event.assert_called_once_with(
        trade_id=repository.save.call_args.args[0].trade_id,
        event="TRADE_SUBMITTED",
    )