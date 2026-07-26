from __future__ import annotations

import streamlit as st

from bootstrap import create_dashboard_service
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


@st.cache_resource
def create_service():
    """
    Construct the dashboard service once per Streamlit
    process instead of rebuilding it on every rerun.
    """
    return create_dashboard_service()


@st.cache_resource
def create_presentation_mapper(
) -> CompleteDashboardPresentationMapper:
    """
    Construct the presentation-mapping graph once per
    Streamlit process.
    """
    return CompleteDashboardPresentationMapper(
        account_mapper=AccountPresentationMapper(),
        scanner_mapper=ScannerPresentationMapper(),
        analytics_mapper=AnalyticsPresentationMapper(),
        trade_history_mapper=(
            TradeHistoryPresentationMapper()
        ),
    )


def load_view_model():
    """
    Load current dashboard data and convert the snapshot
    into the complete presentation model.
    """
    service = create_service()
    presentation_mapper = (
        create_presentation_mapper()
    )

    dashboard_data = (
        service.load_complete_dashboard_data()
    )

    return presentation_mapper.map_dashboard(
        dashboard_data
    )


run_dashboard(
    load_view_model=load_view_model,
    streamlit_module=st,
)