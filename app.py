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
from dashboard.streamlit_renderer import (
    StreamlitDashboardRenderer,
)
from scanner.scanner import scan_market


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
    Construct the dashboard presentation mapper once per
    Streamlit process.
    """

    return CompleteDashboardPresentationMapper(
        account_mapper=AccountPresentationMapper(),
        analytics_mapper=AnalyticsPresentationMapper(),
    )


@st.cache_resource
def create_scanner_mapper():
    """
    Construct the scanner presentation mapper once per
    Streamlit process.
    """

    return ScannerPresentationMapper()


def load_view_model():
    """
    Load backend data and convert it into the presentation
    model used by Streamlit.
    """

    service = create_service()
    mapper = create_mapper()

    dashboard_data = (
        service.load_complete_dashboard_data()
    )

    return mapper.map_dashboard(
        dashboard_data
    )


def load_scanner_view_model():
    """
    Run the market scanner and convert its signals into a
    presentation-ready scanner section.
    """

    signals = scan_market()

    mapper = create_scanner_mapper()

    return mapper.map_scanner_section(
        signals
    )


dashboard_view_model = load_view_model()

renderer = StreamlitDashboardRenderer(
    streamlit_module=st,
)

st.set_page_config(
    page_title="Semi-Auto Trader",
    layout="wide",
)

st.title("Semi-Auto Trader")

renderer.render_account_section(
    dashboard_view_model.account
)

try:
    scanner_view_model = load_scanner_view_model()
except Exception as exc:
    st.error(
        f"Unable to load market scanner: {exc}"
    )
else:
    renderer.render_scanner_section(
        scanner_view_model
    )

renderer.render_analytics_section(
    dashboard_view_model.analytics
)