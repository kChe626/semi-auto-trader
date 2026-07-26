from __future__ import annotations

from unittest.mock import Mock

from dashboard.presentation_models import (
    AccountMetricsViewModel,
    AccountSectionViewModel,
    PositionRowViewModel,
)
from dashboard.streamlit_renderer import (
    StreamlitDashboardRenderer,
)


def make_account_metrics() -> (
    AccountMetricsViewModel
):
    return AccountMetricsViewModel(
        status="ACTIVE",
        cash="$75,000.00",
        equity="$101,250.00",
        buying_power="$300,000.00",
        portfolio_value="$101,250.00",
        daily_change="$1,250.00",
        daily_change_percent="1.25%",
        trading_status="Enabled",
    )


def make_position() -> PositionRowViewModel:
    return PositionRowViewModel(
        symbol="AAPL",
        side="Long",
        quantity="10",
        average_entry_price="$200.00",
        current_price="$205.00",
        market_value="$2,050.00",
        cost_basis="$2,000.00",
        unrealized_profit_loss="$50.00",
        unrealized_profit_loss_percent="2.50%",
    )


def make_streamlit_mock() -> Mock:
    streamlit = Mock()

    streamlit.columns.side_effect = [
        [Mock(), Mock(), Mock(), Mock()],
        [Mock(), Mock()],
    ]

    return streamlit


def test_renderer_displays_account_header() -> None:
    streamlit = make_streamlit_mock()

    renderer = StreamlitDashboardRenderer(
        streamlit_module=streamlit
    )

    account = AccountSectionViewModel(
        metrics=make_account_metrics(),
        positions=(),
        has_open_positions=False,
    )

    renderer.render_account_section(account)

    streamlit.header.assert_called_once_with(
        "Account Overview"
    )


def test_renderer_displays_primary_metrics() -> None:
    streamlit = make_streamlit_mock()

    primary_columns = [
        Mock(),
        Mock(),
        Mock(),
        Mock(),
    ]
    secondary_columns = [Mock(), Mock()]

    streamlit.columns.side_effect = [
        primary_columns,
        secondary_columns,
    ]

    renderer = StreamlitDashboardRenderer(
        streamlit_module=streamlit
    )

    account = AccountSectionViewModel(
        metrics=make_account_metrics(),
        positions=(),
        has_open_positions=False,
    )

    renderer.render_account_section(account)

    primary_columns[0].metric\
        .assert_called_once_with(
            "Portfolio Value",
            "$101,250.00",
            "$1,250.00 (1.25%)",
        )

    primary_columns[1].metric\
        .assert_called_once_with(
            "Equity",
            "$101,250.00",
        )

    primary_columns[2].metric\
        .assert_called_once_with(
            "Cash",
            "$75,000.00",
        )

    primary_columns[3].metric\
        .assert_called_once_with(
            "Buying Power",
            "$300,000.00",
        )


def test_renderer_displays_secondary_metrics() -> None:
    streamlit = make_streamlit_mock()

    primary_columns = [
        Mock(),
        Mock(),
        Mock(),
        Mock(),
    ]
    secondary_columns = [Mock(), Mock()]

    streamlit.columns.side_effect = [
        primary_columns,
        secondary_columns,
    ]

    renderer = StreamlitDashboardRenderer(
        streamlit_module=streamlit
    )

    account = AccountSectionViewModel(
        metrics=make_account_metrics(),
        positions=(make_position(),),
        has_open_positions=True,
    )

    renderer.render_account_section(account)

    secondary_columns[0].metric\
        .assert_called_once_with(
            "Trading Status",
            "Enabled",
        )

    secondary_columns[1].metric\
        .assert_called_once_with(
            "Open Positions",
            "1",
        )


def test_renderer_displays_no_positions_message() -> None:
    streamlit = make_streamlit_mock()

    renderer = StreamlitDashboardRenderer(
        streamlit_module=streamlit
    )

    account = AccountSectionViewModel(
        metrics=make_account_metrics(),
        positions=(),
        has_open_positions=False,
    )

    renderer.render_account_section(account)

    streamlit.info.assert_called_once_with(
        "There are no open positions."
    )

    streamlit.dataframe.assert_not_called()


def test_renderer_displays_position_table() -> None:
    streamlit = make_streamlit_mock()

    renderer = StreamlitDashboardRenderer(
        streamlit_module=streamlit
    )

    account = AccountSectionViewModel(
        metrics=make_account_metrics(),
        positions=(make_position(),),
        has_open_positions=True,
    )

    renderer.render_account_section(account)

    streamlit.dataframe.assert_called_once_with(
        [
            {
                "Symbol": "AAPL",
                "Side": "Long",
                "Quantity": "10",
                "Average Entry Price": "$200.00",
                "Current Price": "$205.00",
                "Market Value": "$2,050.00",
                "Cost Basis": "$2,000.00",
                "Unrealized P/L": "$50.00",
                "Unrealized P/L %": "2.50%",
            }
        ],
        use_container_width=True,
        hide_index=True,
    )


def test_renderer_displays_account_status() -> None:
    streamlit = make_streamlit_mock()

    renderer = StreamlitDashboardRenderer(
        streamlit_module=streamlit
    )

    account = AccountSectionViewModel(
        metrics=make_account_metrics(),
        positions=(),
        has_open_positions=False,
    )

    renderer.render_account_section(account)

    streamlit.caption.assert_called_once_with(
        "Account status: ACTIVE"
    )