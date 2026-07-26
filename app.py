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
from dashboard.streamlit_app import run_dashboard


@st.cache_resource
def create_service():
    """
    Construct the dashboard service once per
    Streamlit process.
    """
    return create_dashboard_service()


@st.cache_resource
def create_mapper():
    """
    Construct the presentation mapper once per
    Streamlit process.
    """
    return CompleteDashboardPresentationMapper(
        account_mapper=AccountPresentationMapper(),
        analytics_mapper=AnalyticsPresentationMapper(),
    )


def load_view_model():
    """
    Load backend data and convert it into the
    presentation model used by Streamlit.
    """
    service = create_service()

    mapper = create_mapper()

    dashboard_data = (
        service.load_complete_dashboard_data()
    )

    return mapper.map_dashboard(
        dashboard_data
    )


run_dashboard(
    load_view_model=load_view_model,
    streamlit_module=st,
)