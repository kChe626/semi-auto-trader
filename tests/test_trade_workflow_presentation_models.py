from dashboard.trade_workflow_presentation_models import (
    TradeWorkflowViewModel,
)


def test_trade_workflow_view_model_stores_display_fields() -> None:
    view_model = TradeWorkflowViewModel(
        symbol="NVDA",
        side="BUY",
        entry_price="$100.00",
        stop_price="$98.00",
        target_price="$104.00",
        quantity="100",
        total_risk="$200.00",
        risk_reward_ratio="2.00",
        status="READY FOR APPROVAL",
        rejection_reasons=(),
    )

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