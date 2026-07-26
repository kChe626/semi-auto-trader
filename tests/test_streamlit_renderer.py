from __future__ import annotations

from unittest.mock import Mock

from dashboard.analytics_chart_models import (
    AnalyticsChartViewModel,
    ChartPointViewModel,
)
from dashboard.analytics_presentation_models import (
    AnalyticsMetricViewModel,
    AnalyticsSectionViewModel,
    AnalyticsTableViewModel,
)
from dashboard.presentation_models import (
    AccountMetricsViewModel,
    AccountSectionViewModel,
    PositionRowViewModel,
)
from dashboard.streamlit_renderer import (
    StreamlitDashboardRenderer,
)


def make_account_metrics() -> AccountMetricsViewModel:
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


def make_empty_table() -> AnalyticsTableViewModel:
    return AnalyticsTableViewModel(
        columns=(),
        rows=(),
    )


def make_empty_chart() -> AnalyticsChartViewModel:
    return AnalyticsChartViewModel(
        title="Equity Curve",
        points=(),
    )


def make_empty_analytics() -> AnalyticsSectionViewModel:
    return AnalyticsSectionViewModel(
        metrics=(),
        equity_curve=make_empty_table(),
        equity_curve_chart=make_empty_chart(),
        drawdown=make_empty_table(),
        monthly_performance=make_empty_table(),
        yearly_performance=make_empty_table(),
        symbol_distribution=make_empty_table(),
        weekday_distribution=make_empty_table(),
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
    streamlit = Mock()

    primary_columns = [
        Mock(),
        Mock(),
        Mock(),
        Mock(),
    ]

    secondary_columns = [
        Mock(),
        Mock(),
    ]

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

    primary_columns[0].metric.assert_called_once_with(
        "Portfolio Value",
        "$101,250.00",
        "$1,250.00 (1.25%)",
    )

    primary_columns[1].metric.assert_called_once_with(
        "Equity",
        "$101,250.00",
    )

    primary_columns[2].metric.assert_called_once_with(
        "Cash",
        "$75,000.00",
    )

    primary_columns[3].metric.assert_called_once_with(
        "Buying Power",
        "$300,000.00",
    )


def test_renderer_displays_secondary_metrics() -> None:
    streamlit = Mock()

    primary_columns = [
        Mock(),
        Mock(),
        Mock(),
        Mock(),
    ]

    secondary_columns = [
        Mock(),
        Mock(),
    ]

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

    secondary_columns[0].metric.assert_called_once_with(
        "Trading Status",
        "Enabled",
    )

    secondary_columns[1].metric.assert_called_once_with(
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


def test_renderer_displays_analytics_header() -> None:
    streamlit = Mock()

    renderer = StreamlitDashboardRenderer(
        streamlit_module=streamlit
    )

    renderer.render_analytics_section(
        make_empty_analytics()
    )

    streamlit.header.assert_called_once_with(
        "Performance Analytics"
    )


def test_renderer_displays_empty_analytics_message() -> None:
    streamlit = Mock()

    renderer = StreamlitDashboardRenderer(
        streamlit_module=streamlit
    )

    renderer.render_analytics_section(
        make_empty_analytics()
    )

    streamlit.info.assert_called_once_with(
        "No closed trades have been recorded yet. "
        "Performance analytics will appear after "
        "the first completed trade."
    )

    streamlit.dataframe.assert_not_called()
    streamlit.line_chart.assert_not_called()


def test_renderer_displays_analytics_metrics() -> None:
    streamlit = Mock()

    metric_columns = [
        Mock(),
        Mock(),
    ]

    streamlit.columns.return_value = metric_columns

    analytics = AnalyticsSectionViewModel(
        metrics=(
            AnalyticsMetricViewModel(
                label="Total Trades",
                value="10",
            ),
            AnalyticsMetricViewModel(
                label="Win Rate",
                value="60.00%",
            ),
        ),
        equity_curve=make_empty_table(),
        equity_curve_chart=make_empty_chart(),
        drawdown=make_empty_table(),
        monthly_performance=make_empty_table(),
        yearly_performance=make_empty_table(),
        symbol_distribution=make_empty_table(),
        weekday_distribution=make_empty_table(),
    )

    renderer = StreamlitDashboardRenderer(
        streamlit_module=streamlit
    )

    renderer.render_analytics_section(
        analytics
    )

    streamlit.columns.assert_called_once_with(2)

    metric_columns[0].metric.assert_called_once_with(
        "Total Trades",
        "10",
    )

    metric_columns[1].metric.assert_called_once_with(
        "Win Rate",
        "60.00%",
    )


def test_renderer_displays_analytics_table() -> None:
    streamlit = Mock()

    equity_curve = AnalyticsTableViewModel(
        columns=(
            "Date",
            "Equity",
        ),
        rows=(
            (
                "2026-07-01",
                "$100,000.00",
            ),
            (
                "2026-07-02",
                "$101,000.00",
            ),
        ),
    )

    analytics = AnalyticsSectionViewModel(
        metrics=(),
        equity_curve=equity_curve,
        equity_curve_chart=make_empty_chart(),
        drawdown=make_empty_table(),
        monthly_performance=make_empty_table(),
        yearly_performance=make_empty_table(),
        symbol_distribution=make_empty_table(),
        weekday_distribution=make_empty_table(),
    )

    renderer = StreamlitDashboardRenderer(
        streamlit_module=streamlit
    )

    renderer.render_analytics_section(
        analytics
    )

    streamlit.subheader.assert_called_once_with(
        "Equity Curve"
    )

    streamlit.dataframe.assert_called_once_with(
        [
            {
                "Date": "2026-07-01",
                "Equity": "$100,000.00",
            },
            {
                "Date": "2026-07-02",
                "Equity": "$101,000.00",
            },
        ],
        use_container_width=True,
        hide_index=True,
    )

    streamlit.line_chart.assert_not_called()


def test_renderer_displays_equity_curve_chart() -> None:
    streamlit = Mock()

    equity_curve = AnalyticsTableViewModel(
        columns=(
            "Date",
            "Equity",
        ),
        rows=(
            (
                "2026-07-01",
                "$100,000.00",
            ),
            (
                "2026-07-02",
                "$101,000.00",
            ),
        ),
    )

    equity_curve_chart = AnalyticsChartViewModel(
        title="Equity Curve",
        points=(
            ChartPointViewModel(
                x="2026-07-01",
                y=100000.0,
            ),
            ChartPointViewModel(
                x="2026-07-02",
                y=101000.0,
            ),
        ),
    )

    analytics = AnalyticsSectionViewModel(
        metrics=(),
        equity_curve=equity_curve,
        equity_curve_chart=equity_curve_chart,
        drawdown=make_empty_table(),
        monthly_performance=make_empty_table(),
        yearly_performance=make_empty_table(),
        symbol_distribution=make_empty_table(),
        weekday_distribution=make_empty_table(),
    )

    renderer = StreamlitDashboardRenderer(
        streamlit_module=streamlit
    )

    renderer.render_analytics_section(
        analytics
    )

    streamlit.line_chart.assert_called_once_with(
        [
            {
                "Date": "2026-07-01",
                "Equity": 100000.0,
            },
            {
                "Date": "2026-07-02",
                "Equity": 101000.0,
            },
        ],
        x="Date",
        y="Equity",
    )

    streamlit.dataframe.assert_called_once()


def test_renderer_skips_empty_equity_curve_chart() -> None:
    streamlit = Mock()

    equity_curve = AnalyticsTableViewModel(
        columns=(
            "Date",
            "Equity",
        ),
        rows=(
            (
                "2026-07-01",
                "$100,000.00",
            ),
        ),
    )

    analytics = AnalyticsSectionViewModel(
        metrics=(),
        equity_curve=equity_curve,
        equity_curve_chart=make_empty_chart(),
        drawdown=make_empty_table(),
        monthly_performance=make_empty_table(),
        yearly_performance=make_empty_table(),
        symbol_distribution=make_empty_table(),
        weekday_distribution=make_empty_table(),
    )

    renderer = StreamlitDashboardRenderer(
        streamlit_module=streamlit
    )

    renderer.render_analytics_section(
        analytics
    )

    streamlit.line_chart.assert_not_called()
    streamlit.dataframe.assert_called_once()