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
from dashboard.trade_history_presentation_models import (
    TradeHistoryRowViewModel,
    TradeHistorySectionViewModel,
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


def make_trade_history_row() -> TradeHistoryRowViewModel:
    return TradeHistoryRowViewModel(
        trade_id="trade-1",
        symbol="AAPL",
        side="LONG",
        opened_at="2026-07-20 14:30 UTC",
        closed_at="2026-07-21 15:31 UTC",
        quantity="10",
        entry_price="$200.00",
        exit_price="$205.00",
        realized_profit_loss="$50.00",
        r_multiple="1.25R",
        holding_duration="1d 1h 1m 1s",
    )


def make_empty_table() -> AnalyticsTableViewModel:
    return AnalyticsTableViewModel(
        columns=(),
        rows=(),
    )


def make_empty_chart(
    title: str = "",
) -> AnalyticsChartViewModel:
    return AnalyticsChartViewModel(
        title=title,
        points=(),
    )


def make_empty_analytics() -> AnalyticsSectionViewModel:
    return AnalyticsSectionViewModel(
        metrics=(),
        equity_curve=make_empty_table(),
        equity_curve_chart=make_empty_chart(
            "Equity Curve"
        ),
        monthly_performance=make_empty_table(),
        monthly_performance_chart=make_empty_chart(
            "Monthly Performance"
        ),
        yearly_performance=make_empty_table(),
        yearly_performance_chart=make_empty_chart(
            "Yearly Performance"
        ),
        drawdown=make_empty_table(),
        drawdown_chart=make_empty_chart(
            "Drawdown"
        ),
        symbol_distribution=make_empty_table(),
        weekday_distribution=make_empty_table(),
    )


def make_analytics(
    *,
    metrics: tuple[
        AnalyticsMetricViewModel,
        ...,
    ] = (),
    equity_curve: AnalyticsTableViewModel | None = None,
    equity_curve_chart: (
        AnalyticsChartViewModel | None
    ) = None,
    monthly_performance: (
        AnalyticsTableViewModel | None
    ) = None,
    monthly_performance_chart: (
        AnalyticsChartViewModel | None
    ) = None,
    yearly_performance: (
        AnalyticsTableViewModel | None
    ) = None,
    yearly_performance_chart: (
        AnalyticsChartViewModel | None
    ) = None,
    drawdown: AnalyticsTableViewModel | None = None,
    drawdown_chart: (
        AnalyticsChartViewModel | None
    ) = None,
    symbol_distribution: (
        AnalyticsTableViewModel | None
    ) = None,
    weekday_distribution: (
        AnalyticsTableViewModel | None
    ) = None,
) -> AnalyticsSectionViewModel:
    return AnalyticsSectionViewModel(
        metrics=metrics,
        equity_curve=(
            equity_curve
            if equity_curve is not None
            else make_empty_table()
        ),
        equity_curve_chart=(
            equity_curve_chart
            if equity_curve_chart is not None
            else make_empty_chart(
                "Equity Curve"
            )
        ),
        monthly_performance=(
            monthly_performance
            if monthly_performance is not None
            else make_empty_table()
        ),
        monthly_performance_chart=(
            monthly_performance_chart
            if monthly_performance_chart is not None
            else make_empty_chart(
                "Monthly Performance"
            )
        ),
        yearly_performance=(
            yearly_performance
            if yearly_performance is not None
            else make_empty_table()
        ),
        yearly_performance_chart=(
            yearly_performance_chart
            if yearly_performance_chart is not None
            else make_empty_chart(
                "Yearly Performance"
            )
        ),
        drawdown=(
            drawdown
            if drawdown is not None
            else make_empty_table()
        ),
        drawdown_chart=(
            drawdown_chart
            if drawdown_chart is not None
            else make_empty_chart(
                "Drawdown"
            )
        ),
        symbol_distribution=(
            symbol_distribution
            if symbol_distribution is not None
            else make_empty_table()
        ),
        weekday_distribution=(
            weekday_distribution
            if weekday_distribution is not None
            else make_empty_table()
        ),
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
    streamlit.bar_chart.assert_not_called()


def test_renderer_displays_analytics_metrics() -> None:
    streamlit = Mock()

    metric_columns = [
        Mock(),
        Mock(),
    ]

    streamlit.columns.return_value = metric_columns

    analytics = make_analytics(
        metrics=(
            AnalyticsMetricViewModel(
                label="Total Trades",
                value="10",
            ),
            AnalyticsMetricViewModel(
                label="Win Rate",
                value="60.00%",
            ),
        )
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

    analytics = make_analytics(
        equity_curve=equity_curve
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


def test_renderer_displays_equity_curve_chart() -> None:
    streamlit = Mock()

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

    analytics = make_analytics(
        equity_curve_chart=equity_curve_chart
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

    streamlit.line_chart.assert_called_once_with(
        [
            {
                "Period": "2026-07-01",
                "Equity Curve": 100000.0,
            },
            {
                "Period": "2026-07-02",
                "Equity Curve": 101000.0,
            },
        ],
        x="Period",
        y="Equity Curve",
    )

    streamlit.bar_chart.assert_not_called()


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

    analytics = make_analytics(
        equity_curve=equity_curve,
        equity_curve_chart=make_empty_chart(
            "Equity Curve"
        ),
    )

    renderer = StreamlitDashboardRenderer(
        streamlit_module=streamlit
    )

    renderer.render_analytics_section(
        analytics
    )

    streamlit.line_chart.assert_not_called()
    streamlit.bar_chart.assert_not_called()


def test_renderer_displays_monthly_performance_chart() -> None:
    streamlit = Mock()

    monthly_performance_chart = AnalyticsChartViewModel(
        title="Monthly Performance",
        points=(
            ChartPointViewModel(
                x="2026-06",
                y=500.0,
            ),
            ChartPointViewModel(
                x="2026-07",
                y=-200.0,
            ),
        ),
    )

    analytics = make_analytics(
        monthly_performance_chart=(
            monthly_performance_chart
        )
    )

    renderer = StreamlitDashboardRenderer(
        streamlit_module=streamlit
    )

    renderer.render_analytics_section(
        analytics
    )

    streamlit.subheader.assert_called_once_with(
        "Monthly Performance"
    )

    streamlit.bar_chart.assert_called_once_with(
        [
            {
                "Period": "2026-06",
                "Monthly Performance": 500.0,
            },
            {
                "Period": "2026-07",
                "Monthly Performance": -200.0,
            },
        ],
        x="Period",
        y="Monthly Performance",
    )

    streamlit.line_chart.assert_not_called()


def test_renderer_skips_empty_monthly_performance_chart() -> None:
    streamlit = Mock()

    monthly_performance = AnalyticsTableViewModel(
        columns=(
            "Month",
            "Realized P/L",
        ),
        rows=(
            (
                "2026-07",
                "$500.00",
            ),
        ),
    )

    analytics = make_analytics(
        monthly_performance=monthly_performance,
        monthly_performance_chart=make_empty_chart(
            "Monthly Performance"
        ),
    )

    renderer = StreamlitDashboardRenderer(
        streamlit_module=streamlit
    )

    renderer.render_analytics_section(
        analytics
    )

    streamlit.line_chart.assert_not_called()
    streamlit.bar_chart.assert_not_called()


def test_renderer_displays_yearly_performance_chart() -> None:
    streamlit = Mock()

    yearly_performance_chart = AnalyticsChartViewModel(
        title="Yearly Performance",
        points=(
            ChartPointViewModel(
                x="2025",
                y=2000.0,
            ),
            ChartPointViewModel(
                x="2026",
                y=3500.0,
            ),
        ),
    )

    analytics = make_analytics(
        yearly_performance_chart=(
            yearly_performance_chart
        )
    )

    renderer = StreamlitDashboardRenderer(
        streamlit_module=streamlit
    )

    renderer.render_analytics_section(
        analytics
    )

    streamlit.subheader.assert_called_once_with(
        "Yearly Performance"
    )

    streamlit.bar_chart.assert_called_once_with(
        [
            {
                "Period": "2025",
                "Yearly Performance": 2000.0,
            },
            {
                "Period": "2026",
                "Yearly Performance": 3500.0,
            },
        ],
        x="Period",
        y="Yearly Performance",
    )

    streamlit.line_chart.assert_not_called()


def test_renderer_skips_empty_yearly_performance_chart() -> None:
    streamlit = Mock()

    yearly_performance = AnalyticsTableViewModel(
        columns=(
            "Year",
            "Realized P/L",
        ),
        rows=(
            (
                "2026",
                "$3,500.00",
            ),
        ),
    )

    analytics = make_analytics(
        yearly_performance=yearly_performance,
        yearly_performance_chart=make_empty_chart(
            "Yearly Performance"
        ),
    )

    renderer = StreamlitDashboardRenderer(
        streamlit_module=streamlit
    )

    renderer.render_analytics_section(
        analytics
    )

    streamlit.line_chart.assert_not_called()
    streamlit.bar_chart.assert_not_called()


def test_renderer_displays_drawdown_chart() -> None:
    streamlit = Mock()

    drawdown_chart = AnalyticsChartViewModel(
        title="Drawdown",
        points=(
            ChartPointViewModel(
                x="2026-07-01",
                y=0.0,
            ),
            ChartPointViewModel(
                x="2026-07-02",
                y=-500.0,
            ),
        ),
    )

    analytics = make_analytics(
        drawdown_chart=drawdown_chart
    )

    renderer = StreamlitDashboardRenderer(
        streamlit_module=streamlit
    )

    renderer.render_analytics_section(
        analytics
    )

    streamlit.subheader.assert_called_once_with(
        "Drawdown"
    )

    streamlit.line_chart.assert_called_once_with(
        [
            {
                "Period": "2026-07-01",
                "Drawdown": 0.0,
            },
            {
                "Period": "2026-07-02",
                "Drawdown": -500.0,
            },
        ],
        x="Period",
        y="Drawdown",
    )

    streamlit.bar_chart.assert_not_called()


def test_renderer_skips_empty_drawdown_chart() -> None:
    streamlit = Mock()

    drawdown = AnalyticsTableViewModel(
        columns=(
            "Date",
            "Drawdown",
        ),
        rows=(
            (
                "2026-07-02",
                "-$500.00",
            ),
        ),
    )

    analytics = make_analytics(
        drawdown=drawdown,
        drawdown_chart=make_empty_chart(
            "Drawdown"
        ),
    )

    renderer = StreamlitDashboardRenderer(
        streamlit_module=streamlit
    )

    renderer.render_analytics_section(
        analytics
    )

    streamlit.line_chart.assert_not_called()
    streamlit.bar_chart.assert_not_called()


def test_renderer_displays_trade_history_table() -> None:
    streamlit = Mock()

    renderer = StreamlitDashboardRenderer(
        streamlit_module=streamlit
    )

    trade_history = TradeHistorySectionViewModel(
        rows=(
            make_trade_history_row(),
        ),
    )

    renderer.render_trade_history_section(
        trade_history
    )

    streamlit.header.assert_called_once_with(
        "Trade History"
    )

    streamlit.dataframe.assert_called_once_with(
        [
            {
                "Trade ID": "trade-1",
                "Symbol": "AAPL",
                "Side": "LONG",
                "Opened At": (
                    "2026-07-20 14:30 UTC"
                ),
                "Closed At": (
                    "2026-07-21 15:31 UTC"
                ),
                "Quantity": "10",
                "Entry Price": "$200.00",
                "Exit Price": "$205.00",
                "Realized P/L": "$50.00",
                "R Multiple": "1.25R",
                "Holding Duration": (
                    "1d 1h 1m 1s"
                ),
            }
        ],
        use_container_width=True,
        hide_index=True,
    )

    streamlit.info.assert_not_called()


def test_renderer_displays_empty_trade_history_message() -> None:
    streamlit = Mock()

    renderer = StreamlitDashboardRenderer(
        streamlit_module=streamlit
    )

    trade_history = TradeHistorySectionViewModel(
        rows=(),
    )

    renderer.render_trade_history_section(
        trade_history
    )

    streamlit.header.assert_called_once_with(
        "Trade History"
    )

    streamlit.info.assert_called_once_with(
        "No completed trades available."
    )

    streamlit.dataframe.assert_not_called()