from unittest.mock import Mock, call

from dashboard.streamlit_renderer import StreamlitRenderer
from dashboard.trade_workflow_presentation_models import (
    TradeWorkflowViewModel,
)


def test_render_trade_workflow_ready_for_approval() -> None:
    streamlit = Mock()

    renderer = StreamlitRenderer(
        streamlit_module=streamlit,
    )

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

    renderer.render_trade_workflow(view_model)

    streamlit.subheader.assert_called_once_with(
        "Trade Approval"
    )
    streamlit.success.assert_called_once_with(
        "READY FOR APPROVAL"
    )
    streamlit.write.assert_has_calls(
        [
            call("Symbol: NVDA"),
            call("Side: BUY"),
            call("Entry: $100.00"),
            call("Stop: $98.00"),
            call("Target: $104.00"),
            call("Quantity: 100"),
            call("Total Risk: $200.00"),
            call("Risk/Reward: 2.00"),
        ]
    )


def test_render_trade_workflow_rejected() -> None:
    streamlit = Mock()

    renderer = StreamlitRenderer(
        streamlit_module=streamlit,
    )

    view_model = TradeWorkflowViewModel(
        symbol="NVDA",
        side="BUY",
        entry_price="$100.00",
        stop_price="$98.00",
        target_price="$104.00",
        quantity="100",
        total_risk="$200.00",
        risk_reward_ratio="2.00",
        status="REJECTED",
        rejection_reasons=(
            "Market is closed.",
            "An open order already exists for NVDA.",
        ),
    )

    renderer.render_trade_workflow(view_model)

    streamlit.subheader.assert_called_once_with(
        "Trade Approval"
    )
    streamlit.error.assert_called_once_with(
        "REJECTED"
    )
    streamlit.write.assert_has_calls(
        [
            call("Symbol: NVDA"),
            call("Side: BUY"),
            call("Entry: $100.00"),
            call("Stop: $98.00"),
            call("Target: $104.00"),
            call("Quantity: 100"),
            call("Total Risk: $200.00"),
            call("Risk/Reward: 2.00"),
        ]
    )
    streamlit.warning.assert_has_calls(
        [
            call("Market is closed."),
            call(
                "An open order already exists for NVDA."
            ),
        ]
    )