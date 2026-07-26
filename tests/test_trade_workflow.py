from unittest.mock import Mock

from application.trade_workflow import TradeWorkflow
from models.preflight_result import PreflightResult
from models.trade_plan import TradePlan
from models.trade_signal import TradeSignal


def create_test_signal() -> TradeSignal:
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


def create_test_plan(
    quantity: int = 500,
) -> TradePlan:
    return TradePlan(
        symbol="NVDA",
        signal_type="BUY",
        entry_price=100.00,
        stop_price=98.00,
        target_price=104.00,
        quantity=quantity,
        risk_per_share=2.00,
        reward_per_share=4.00,
        total_risk=quantity * 2.00,
        risk_reward_ratio=2.00,
        rsi=55.00,
        short_sma=101.00,
        long_sma=99.00,
    )


def test_prepare_trade_returns_approval_ready_result() -> None:
    signal = create_test_signal()
    original_plan = create_test_plan(quantity=500)
    limited_plan = create_test_plan(quantity=100)

    plan_builder = Mock(
        return_value=original_plan
    )
    risk_limiter = Mock(
        return_value=limited_plan
    )
    preflight_runner = Mock(
        return_value=PreflightResult(
            approved=True,
            reasons=[],
        )
    )

    workflow = TradeWorkflow(
        account_equity=100_000.00,
        risk_percent=0.01,
        max_position_percent=0.10,
        stop_loss_percent=0.02,
        reward_risk_ratio=2.00,
        plan_builder=plan_builder,
        risk_limiter=risk_limiter,
        preflight_runner=preflight_runner,
    )

    result = workflow.prepare_trade(signal)

    assert result.ready_for_approval is True
    assert result.plan is limited_plan
    assert result.preflight.approved is True
    assert result.preflight.reasons == []

    plan_builder.assert_called_once_with(
        signal=signal,
        account_equity=100_000.00,
        risk_percent=0.01,
        stop_loss_percent=0.02,
        reward_risk_ratio=2.00,
        atr_multiplier=None,
    )
    risk_limiter.assert_called_once_with(
        original_plan,
        account_equity=100_000.00,
        max_position_percent=0.10,
    )
    preflight_runner.assert_called_once_with(
        limited_plan
    )


def test_prepare_trade_returns_rejection_reasons() -> None:
    signal = create_test_signal()
    plan = create_test_plan(quantity=100)

    plan_builder = Mock(return_value=plan)
    risk_limiter = Mock(return_value=plan)
    preflight_runner = Mock(
        return_value=PreflightResult(
            approved=False,
            reasons=[
                "Market is closed.",
                "An open order already exists for NVDA.",
            ],
        )
    )

    workflow = TradeWorkflow(
        account_equity=100_000.00,
        risk_percent=0.01,
        max_position_percent=0.10,
        stop_loss_percent=0.02,
        plan_builder=plan_builder,
        risk_limiter=risk_limiter,
        preflight_runner=preflight_runner,
    )

    result = workflow.prepare_trade(signal)

    assert result.ready_for_approval is False
    assert result.plan is plan
    assert result.preflight.approved is False
    assert result.preflight.reasons == [
        "Market is closed.",
        "An open order already exists for NVDA.",
    ]


def test_prepare_trade_passes_atr_configuration() -> None:
    signal = create_test_signal()
    plan = create_test_plan(quantity=100)

    plan_builder = Mock(return_value=plan)
    risk_limiter = Mock(return_value=plan)
    preflight_runner = Mock(
        return_value=PreflightResult(
            approved=True,
            reasons=[],
        )
    )

    workflow = TradeWorkflow(
        account_equity=100_000.00,
        risk_percent=0.01,
        max_position_percent=0.10,
        atr_multiplier=2.00,
        reward_risk_ratio=3.00,
        plan_builder=plan_builder,
        risk_limiter=risk_limiter,
        preflight_runner=preflight_runner,
    )

    workflow.prepare_trade(signal)

    plan_builder.assert_called_once_with(
        signal=signal,
        account_equity=100_000.00,
        risk_percent=0.01,
        stop_loss_percent=None,
        reward_risk_ratio=3.00,
        atr_multiplier=2.00,
    )