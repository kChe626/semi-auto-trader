from __future__ import annotations

from unittest.mock import Mock, patch

from dashboard.streamlit_app import run_dashboard


def _build_view_model() -> Mock:
    view_model = Mock()

    view_model.account = Mock(
        name="account-view-model"
    )
    view_model.scanner = Mock(
        name="scanner-view-model"
    )
    view_model.workflow = Mock(
        name="workflow-view-model"
    )
    view_model.analytics = Mock(
        name="analytics-view-model"
    )
    view_model.trade_history = Mock(
        name="trade-history-view-model"
    )

    return view_model


@patch(
    "dashboard.streamlit_app."
    "StreamlitDashboardRenderer"
)
def test_app_configures_streamlit_page(
    renderer_class: Mock,
) -> None:
    streamlit = Mock()
    load_view_model = Mock(
        return_value=_build_view_model()
    )

    run_dashboard(
        load_view_model=load_view_model,
        streamlit_module=streamlit,
    )

    streamlit.set_page_config.assert_called_once_with(
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
    load_view_model = Mock(
        return_value=_build_view_model()
    )

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
def test_app_loads_and_renders_dashboard(
    renderer_class: Mock,
) -> None:
    streamlit = Mock()
    view_model = _build_view_model()

    load_view_model = Mock(
        return_value=view_model
    )

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

    renderer.render_scanner_section\
        .assert_called_once_with(
            view_model.scanner
        )

    renderer.render_trade_workflow\
        .assert_called_once_with(
            view_model.workflow
        )

    renderer.render_analytics_section\
        .assert_called_once_with(
            view_model.analytics
        )

    renderer.render_trade_history_section\
        .assert_called_once_with(
            view_model.trade_history
        )


@patch(
    "dashboard.streamlit_app."
    "StreamlitDashboardRenderer"
)
def test_app_renders_sections_in_expected_order(
    renderer_class: Mock,
) -> None:
    streamlit = Mock()
    view_model = _build_view_model()

    load_view_model = Mock(
        return_value=view_model
    )

    renderer = renderer_class.return_value

    call_order: list[str] = []

    renderer.render_account_section.side_effect = (
        lambda account: call_order.append(
            "account"
        )
    )

    renderer.render_scanner_section.side_effect = (
        lambda scanner: call_order.append(
            "scanner"
        )
    )

    renderer.render_trade_workflow.side_effect = (
        lambda workflow: call_order.append(
            "workflow"
        )
    )

    renderer.render_analytics_section.side_effect = (
        lambda analytics: call_order.append(
            "analytics"
        )
    )

    renderer.render_trade_history_section\
        .side_effect = (
            lambda trade_history: call_order.append(
                "trade_history"
            )
        )

    run_dashboard(
        load_view_model=load_view_model,
        streamlit_module=streamlit,
    )

    assert call_order == [
        "account",
        "scanner",
        "workflow",
        "analytics",
        "trade_history",
    ]


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

    streamlit.title.assert_called_once_with(
        "Semi-Auto Trader Dashboard"
    )

    streamlit.error.assert_called_once_with(
        "Dashboard data could not be loaded: "
        "database unavailable"
    )

    streamlit.header.assert_not_called()
    streamlit.subheader.assert_not_called()
    streamlit.dataframe.assert_not_called()