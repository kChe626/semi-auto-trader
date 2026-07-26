from dashboard.trade_workflow_presentation_mapper import (
    TradeWorkflowPresentationMapper,
)
from models.preflight_result import PreflightResult
from models.trade_plan import TradePlan
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