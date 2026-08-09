from dashboard.trade_workflow_presentation_mapper import (
    TradeWorkflowPresentationMapper,
)
from models.preflight_result import PreflightResult
from models.trade_plan import TradePlan
from models.trade_signal import TradeSignal
from models.workflow_result import WorkflowResult


def create_test_plan() -> TradePlan:
    return TradePlan(
        symbol="NVDA",
        signal_type="BUY",
        entry_price=100.00,
        stop_price=98.00,
        target_price=104.00,
        quantity=100,
        risk_per_share=2.00,
        reward_per_share=4.00,
        total_risk=200.00,
        risk_reward_ratio=2.00,
    )


def test_maps_approval_ready_workflow() -> None:
    result = WorkflowResult(
        ready_for_approval=True,
        plan=create_test_plan(),
        preflight=PreflightResult(
            approved=True,
            reasons=[],
        ),
    )

    mapper = TradeWorkflowPresentationMapper()

    view_model = mapper.map(result)

    assert view_model.symbol == "NVDA"
    assert view_model.side == "BUY"
    assert view_model.entry_price == "$100.00"
    assert view_model.stop_price == "$98.00"
    assert view_model.target_price == "$104.00"
    assert view_model.quantity == "100"
    assert view_model.total_risk == "$200.00"
    assert view_model.risk_reward_ratio == "2.00"
    assert view_model.status == "READY FOR APPROVAL"
    assert view_model.rejection_reasons == ()


def test_maps_rejected_workflow() -> None:
    result = WorkflowResult(
        ready_for_approval=False,
        plan=create_test_plan(),
        preflight=PreflightResult(
            approved=False,
            reasons=[
                "Market is closed.",
                "An open order already exists for NVDA.",
            ],
        ),
    )

    mapper = TradeWorkflowPresentationMapper()

    view_model = mapper.map(result)

    assert view_model.status == "REJECTED"

    assert view_model.rejection_reasons == (
        "Market is closed.",
        "An open order already exists for NVDA.",
    )


def test_none_maps_to_no_eligible_trade() -> None:
    mapper = TradeWorkflowPresentationMapper()

    result = mapper.map(None)

    assert result.symbol == "—"
    assert result.side == "—"
    assert result.score == "—"
    assert result.status == "NO ELIGIBLE TRADE"

    assert result.rejection_reasons == (
        "No trade signals were found "
        "by the scanner.",
    )


def test_sell_signals_explain_short_trades_disabled(
) -> None:
    mapper = TradeWorkflowPresentationMapper()

    signals = (
        TradeSignal(
            symbol="MS",
            signal_type="SELL",
            price=216.33,
            reason=(
                "Bearish SMA crossover "
                "confirmed by RSI 51.84"
            ),
        ),
        TradeSignal(
            symbol="HOOD",
            signal_type="SELL",
            price=93.29,
            reason=(
                "Bearish SMA crossover "
                "confirmed by RSI 45.68"
            ),
        ),
    )

    result = mapper.map(
        None,
        scanner_signals=signals,
    )

    assert result.status == "NO ELIGIBLE TRADE"

    assert result.rejection_reasons == (
        (
            "MS: SELL signal was excluded because "
            "short trades are disabled."
        ),
        (
            "HOOD: SELL signal was excluded because "
            "short trades are disabled."
        ),
    )


def test_unexplained_signals_use_filter_summary() -> None:
    mapper = TradeWorkflowPresentationMapper()

    signals = (
        TradeSignal(
            symbol="AAPL",
            signal_type="BUY",
            price=200.00,
            reason="Bullish test signal",
        ),
    )

    result = mapper.map(
        None,
        scanner_signals=signals,
    )

    assert result.status == "NO ELIGIBLE TRADE"

    assert result.rejection_reasons == (
        (
            "Scanner signals were found, but no "
            "candidate remained after direction, "
            "risk, preflight, and minimum-score "
            "filters."
        ),
    )


def test_score_is_formatted_when_available() -> None:
    workflow = WorkflowResult(
        ready_for_approval=True,
        plan=create_test_plan(),
        preflight=PreflightResult(
            approved=True,
            reasons=[],
        ),
        score=82.456,
    )

    mapper = TradeWorkflowPresentationMapper()

    result = mapper.map(workflow)

    assert result.score == "82.46"


def test_missing_score_uses_dash() -> None:
    workflow = WorkflowResult(
        ready_for_approval=True,
        plan=create_test_plan(),
        preflight=PreflightResult(
            approved=True,
            reasons=[],
        ),
        score=None,
    )

    mapper = TradeWorkflowPresentationMapper()

    result = mapper.map(workflow)

    assert result.score == "—"