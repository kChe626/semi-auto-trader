from __future__ import annotations

import streamlit as st

from bootstrap import (
    create_dashboard_approval_service,
    create_dashboard_service,
)
from dashboard.analytics_presentation_mapper import (
    AnalyticsPresentationMapper,
)
from dashboard.complete_presentation_mapper import (
    CompleteDashboardPresentationMapper,
)
from dashboard.presentation_mapper import (
    AccountPresentationMapper,
)
from dashboard.scanner_presentation_mapper import (
    ScannerPresentationMapper,
)
from dashboard.streamlit_app import run_dashboard
from dashboard.trade_history_presentation_mapper import (
    TradeHistoryPresentationMapper,
)
from dashboard.trade_workflow_presentation_mapper import (
    TradeWorkflowPresentationMapper,
)
from models.workflow_result import WorkflowResult


_latest_workflow_result: WorkflowResult | None = None


def create_service():
    """
    Construct a fresh dashboard service for the
    current dashboard load.

    The service is intentionally not cached so that
    scanner results, workflow selection, broker state,
    and trading configuration remain current.
    """
    return create_dashboard_service()


@st.cache_resource
def create_approval_service():
    """
    Construct the dashboard paper-trade approval
    service once per Streamlit process.
    """
    return create_dashboard_approval_service()


@st.cache_resource
def create_presentation_mapper(
) -> CompleteDashboardPresentationMapper:
    """
    Construct the presentation-mapping graph once per
    Streamlit process.

    These mappers are stateless and safe to cache.
    """
    return CompleteDashboardPresentationMapper(
        account_mapper=AccountPresentationMapper(),
        scanner_mapper=ScannerPresentationMapper(),
        workflow_mapper=(
            TradeWorkflowPresentationMapper()
        ),
        analytics_mapper=(
            AnalyticsPresentationMapper()
        ),
        trade_history_mapper=(
            TradeHistoryPresentationMapper()
        ),
    )


def load_view_model():
    """
    Load current dashboard data and convert the
    snapshot into the complete presentation model.

    The selected backend workflow is retained so
    approval executes the real WorkflowResult rather
    than formatted presentation data.
    """
    global _latest_workflow_result

    service = create_service()

    presentation_mapper = (
        create_presentation_mapper()
    )

    dashboard_data = (
        service.load_complete_dashboard_data()
    )

    _latest_workflow_result = (
        dashboard_data.workflow_result
    )

    return presentation_mapper.map_dashboard(
        dashboard_data
    )


def approve_trade(
    _workflow_view_model,
) -> None:
    """
    Approve the currently selected backend workflow.

    The presentation view model is intentionally not
    used for broker execution.
    """
    workflow_result = (
        _latest_workflow_result
    )

    if workflow_result is None:
        st.error(
            "No eligible trade workflow is available."
        )
        return

    approval_service = (
        create_approval_service()
    )

    try:
        order = approval_service.approve(
            workflow_result
        )
    except Exception as error:
        st.error(
            "Trade approval failed: "
            f"{error}"
        )
        return

    order_id = getattr(
        order,
        "id",
        "Unavailable",
    )

    st.success(
        "Paper order submitted successfully. "
        f"Order ID: {order_id}"
    )


def reject_trade(
    _workflow_view_model,
) -> None:
    """
    Rejecting a dashboard candidate performs no
    broker action.
    """
    st.info(
        "Trade rejected. No order was submitted."
    )


run_dashboard(
    load_view_model=load_view_model,
    streamlit_module=st,
    approve_trade=approve_trade,
    reject_trade=reject_trade,
)