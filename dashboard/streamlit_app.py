from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol

from dashboard.complete_presentation_models import (
    CompleteDashboardViewModel,
)
from dashboard.streamlit_renderer import (
    StreamlitDashboardRenderer,
)
from dashboard.trade_workflow_presentation_models import (
    TradeWorkflowViewModel,
)


class StreamlitAppProtocol(Protocol):
    def set_page_config(
        self,
        **kwargs: Any,
    ) -> Any:
        ...

    def title(
        self,
        body: str,
    ) -> Any:
        ...

    def error(
        self,
        body: str,
    ) -> Any:
        ...


DashboardViewModelLoader = Callable[
    [],
    CompleteDashboardViewModel,
]

TradeWorkflowAction = Callable[
    [TradeWorkflowViewModel],
    None,
]


def _do_nothing(
    workflow: TradeWorkflowViewModel,
) -> None:
    """
    Default safe action used when no workflow
    action has been injected.
    """
    return None


def run_dashboard(
    *,
    load_view_model: DashboardViewModelLoader,
    streamlit_module: StreamlitAppProtocol,
    approve_trade: TradeWorkflowAction = _do_nothing,
    reject_trade: TradeWorkflowAction = _do_nothing,
) -> None:
    """
    Run the Streamlit dashboard.

    Dependencies are injected so the application
    remains independently testable.
    """

    streamlit_module.set_page_config(
        page_title="Semi-Auto Trader",
        page_icon="📈",
        layout="wide",
    )

    streamlit_module.title(
        "Semi-Auto Trader Dashboard"
    )

    try:
        view_model = load_view_model()
    except Exception as error:
        streamlit_module.error(
            "Dashboard data could not be loaded: "
            f"{error}"
        )
        return

    renderer = StreamlitDashboardRenderer(
        streamlit_module=streamlit_module
    )

    def on_approve() -> None:
        if (
            view_model.workflow.status
            != "READY FOR APPROVAL"
        ):
            streamlit_module.error(
                "Trade cannot be approved because "
                "it is not ready for approval."
            )
            return

        approve_trade(
            view_model.workflow
        )

    def on_reject() -> None:
        reject_trade(
            view_model.workflow
        )

    renderer.render_account_section(
        view_model.account
    )

    renderer.render_scanner_section(
        view_model.scanner
    )

    renderer.render_trade_workflow(
        view_model.workflow,
        on_approve=on_approve,
        on_reject=on_reject,
    )

    renderer.render_analytics_section(
        view_model.analytics
    )

    renderer.render_trade_history_section(
        view_model.trade_history
    )