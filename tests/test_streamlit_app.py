from __future__ import annotations

from unittest.mock import Mock, patch

from dashboard.streamlit_app import run_dashboard


@patch(
    "dashboard.streamlit_app."
    "StreamlitDashboardRenderer"
)
def test_app_configures_streamlit_page(
    renderer_class: Mock,
) -> None:
    streamlit = Mock()
    load_view_model = Mock()

    view_model = Mock()
    view_model.account = Mock()

    load_view_model.return_value = view_model

    run_dashboard(
        load_view_model=load_view_model,
        streamlit_module=streamlit,
    )

    streamlit.set_page_config\
        .assert_called_once_with(
            page_title="Semi-Auto Trader",
            page_icon="📈",
            layout="wide",
        )

    renderer_class.assert_called_once_with(
        streamlit_module=streamlit
    )


@patch(
    "dashboard.streamlit_app."
    "StreamlitDashboardRenderer"
)
def test_app_displays_dashboard_title(
    renderer_class: Mock,
) -> None:
    streamlit = Mock()
    load_view_model = Mock()

    view_model = Mock()
    view_model.account = Mock()

    load_view_model.return_value = view_model

    run_dashboard(
        load_view_model=load_view_model,
        streamlit_module=streamlit,
    )

    streamlit.title.assert_called_once_with(
        "Semi-Auto Trader Dashboard"
    )

    renderer_class.assert_called_once_with(
        streamlit_module=streamlit
    )


@patch(
    "dashboard.streamlit_app."
    "StreamlitDashboardRenderer"
)
def test_app_loads_and_renders_account(
    renderer_class: Mock,
) -> None:
    streamlit = Mock()
    load_view_model = Mock()

    view_model = Mock()
    view_model.account = Mock(
        name="account-view-model"
    )

    load_view_model.return_value = view_model

    renderer = renderer_class.return_value

    run_dashboard(
        load_view_model=load_view_model,
        streamlit_module=streamlit,
    )

    load_view_model.assert_called_once_with()

    renderer_class.assert_called_once_with(
        streamlit_module=streamlit
    )

    renderer.render_account_section\
        .assert_called_once_with(
            view_model.account
        )


@patch(
    "dashboard.streamlit_app."
    "StreamlitDashboardRenderer"
)
def test_app_displays_loading_error(
    renderer_class: Mock,
) -> None:
    streamlit = Mock()
    load_view_model = Mock(
        side_effect=RuntimeError(
            "Alpaca unavailable"
        )
    )

    run_dashboard(
        load_view_model=load_view_model,
        streamlit_module=streamlit,
    )

    streamlit.error.assert_called_once_with(
        "Dashboard data could not be loaded: "
        "Alpaca unavailable"
    )

    renderer_class.assert_not_called()


def test_app_stops_after_loading_error() -> None:
    streamlit = Mock()
    load_view_model = Mock(
        side_effect=ValueError(
            "database unavailable"
        )
    )

    run_dashboard(
        load_view_model=load_view_model,
        streamlit_module=streamlit,
    )

    streamlit.title.assert_called_once()
    streamlit.error.assert_called_once()