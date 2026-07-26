from __future__ import annotations

from typing import Any, Protocol, Sequence

from dashboard.analytics_chart_models import (
    AnalyticsChartViewModel,
)
from dashboard.analytics_presentation_models import (
    AnalyticsSectionViewModel,
    AnalyticsTableViewModel,
)
from dashboard.presentation_models import (
    AccountSectionViewModel,
)
from dashboard.scanner_presentation_models import (
    ScannerSectionViewModel,
)
from dashboard.trade_history_presentation_models import (
    TradeHistorySectionViewModel,
)


class MetricContainerProtocol(Protocol):
    def metric(
        self,
        label: str,
        value: str,
        delta: str | None = None,
    ) -> Any:
        ...


class StreamlitProtocol(Protocol):
    def header(self, body: str) -> Any:
        ...

    def subheader(self, body: str) -> Any:
        ...

    def columns(
        self,
        spec: int,
    ) -> Sequence[MetricContainerProtocol]:
        ...

    def dataframe(
        self,
        data: Any,
        *,
        use_container_width: bool,
        hide_index: bool,
    ) -> Any:
        ...

    def line_chart(
        self,
        data: Any,
        *,
        x: str,
        y: str,
    ) -> Any:
        ...

    def bar_chart(
        self,
        data: Any,
        *,
        x: str,
        y: str,
    ) -> Any:
        ...

    def info(self, body: str) -> Any:
        ...

    def caption(self, body: str) -> Any:
        ...


class StreamlitDashboardRenderer:
    """
    Render presentation-ready dashboard models.

    This class does not access Alpaca, SQLite, analytics
    services, scanner services, or trade execution services.
    """

    def __init__(
        self,
        *,
        streamlit_module: StreamlitProtocol,
    ) -> None:
        self._st = streamlit_module

    def render_account_section(
        self,
        account: AccountSectionViewModel,
    ) -> None:
        self._st.header("Account Overview")

        self._render_primary_metrics(account)
        self._render_secondary_metrics(account)

        self._st.caption(
            f"Account status: {account.metrics.status}"
        )

        self._render_positions(account)

    def render_scanner_section(
        self,
        scanner: ScannerSectionViewModel,
    ) -> None:
        """
        Render market scanner signals.
        """

        self._st.header("Market Scanner")

        if not scanner.has_results:
            self._st.info(
                "No trade signals were found."
            )
            return

        rows = [
            {
                "Symbol": result.symbol,
                "Signal": result.signal,
                "Price": result.price,
                "Short SMA": result.short_sma,
                "Long SMA": result.long_sma,
                "RSI": result.rsi,
                "ATR": result.atr,
                "Reason": result.reason,
            }
            for result in scanner.results
        ]

        self._st.dataframe(
            rows,
            use_container_width=True,
            hide_index=True,
        )

    def render_analytics_section(
        self,
        analytics: AnalyticsSectionViewModel,
    ) -> None:
        """
        Render closed-trade performance analytics.
        """

        self._st.header("Performance Analytics")

        self._render_analytics_metrics(analytics)

        if self._analytics_is_empty(analytics):
            self._st.info(
                "No closed trades have been recorded yet. "
                "Performance analytics will appear after "
                "the first completed trade."
            )
            return

        self._render_chart(
            analytics.equity_curve_chart
        )

        self._render_analytics_table(
            title="Equity Curve",
            table=analytics.equity_curve,
        )

        self._render_bar_chart(
            analytics.monthly_performance_chart
        )

        self._render_analytics_table(
            title="Monthly Performance",
            table=analytics.monthly_performance,
        )

        self._render_bar_chart(
            analytics.yearly_performance_chart
        )

        self._render_analytics_table(
            title="Yearly Performance",
            table=analytics.yearly_performance,
        )

        self._render_chart(
            analytics.drawdown_chart
        )

        self._render_analytics_table(
            title="Drawdown",
            table=analytics.drawdown,
        )

        self._render_analytics_table(
            title="Trades by Symbol",
            table=analytics.symbol_distribution,
        )

        self._render_analytics_table(
            title="Trades by Weekday",
            table=analytics.weekday_distribution,
        )

    def render_trade_history_section(
        self,
        trade_history: TradeHistorySectionViewModel,
    ) -> None:
        """
        Render completed-trade history.
        """

        self._st.header("Trade History")

        if not trade_history.has_rows:
            self._st.info(
                "No completed trades available."
            )
            return

        rows = [
            {
                "Trade ID": row.trade_id,
                "Symbol": row.symbol,
                "Side": row.side,
                "Opened At": row.opened_at,
                "Closed At": row.closed_at,
                "Quantity": row.quantity,
                "Entry Price": row.entry_price,
                "Exit Price": row.exit_price,
                "Realized P/L": (
                    row.realized_profit_loss
                ),
                "R Multiple": row.r_multiple,
                "Holding Duration": (
                    row.holding_duration
                ),
            }
            for row in trade_history.rows
        ]

        self._st.dataframe(
            rows,
            use_container_width=True,
            hide_index=True,
        )

    def _render_primary_metrics(
        self,
        account: AccountSectionViewModel,
    ) -> None:
        columns = self._st.columns(4)

        columns[0].metric(
            "Portfolio Value",
            account.metrics.portfolio_value,
            (
                f"{account.metrics.daily_change} "
                f"({account.metrics.daily_change_percent})"
            ),
        )

        columns[1].metric(
            "Equity",
            account.metrics.equity,
        )

        columns[2].metric(
            "Cash",
            account.metrics.cash,
        )

        columns[3].metric(
            "Buying Power",
            account.metrics.buying_power,
        )

    def _render_secondary_metrics(
        self,
        account: AccountSectionViewModel,
    ) -> None:
        columns = self._st.columns(2)

        columns[0].metric(
            "Trading Status",
            account.metrics.trading_status,
        )

        columns[1].metric(
            "Open Positions",
            str(len(account.positions)),
        )

    def _render_positions(
        self,
        account: AccountSectionViewModel,
    ) -> None:
        self._st.subheader("Open Positions")

        if not account.has_open_positions:
            self._st.info(
                "There are no open positions."
            )
            return

        rows = [
            {
                "Symbol": position.symbol,
                "Side": position.side,
                "Quantity": position.quantity,
                "Average Entry Price": (
                    position.average_entry_price
                ),
                "Current Price": (
                    position.current_price
                ),
                "Market Value": (
                    position.market_value
                ),
                "Cost Basis": position.cost_basis,
                "Unrealized P/L": (
                    position.unrealized_profit_loss
                ),
                "Unrealized P/L %": (
                    position
                    .unrealized_profit_loss_percent
                ),
            }
            for position in account.positions
        ]

        self._st.dataframe(
            rows,
            use_container_width=True,
            hide_index=True,
        )

    def _render_analytics_metrics(
        self,
        analytics: AnalyticsSectionViewModel,
    ) -> None:
        metrics = analytics.metrics

        if not metrics:
            return

        for start_index in range(
            0,
            len(metrics),
            4,
        ):
            metric_group = metrics[
                start_index:start_index + 4
            ]

            columns = self._st.columns(
                len(metric_group)
            )

            for column, metric in zip(
                columns,
                metric_group,
                strict=True,
            ):
                column.metric(
                    metric.label,
                    metric.value,
                )

    def _render_chart(
        self,
        chart: AnalyticsChartViewModel,
    ) -> None:
        if not chart.points:
            return

        rows = [
            {
                "Period": point.x,
                chart.title: point.y,
            }
            for point in chart.points
        ]

        self._st.subheader(chart.title)

        self._st.line_chart(
            rows,
            x="Period",
            y=chart.title,
        )

    def _render_bar_chart(
        self,
        chart: AnalyticsChartViewModel,
    ) -> None:
        if not chart.points:
            return

        rows = [
            {
                "Period": point.x,
                chart.title: point.y,
            }
            for point in chart.points
        ]

        self._st.subheader(chart.title)

        self._st.bar_chart(
            rows,
            x="Period",
            y=chart.title,
        )

    def _render_analytics_table(
        self,
        *,
        title: str,
        table: AnalyticsTableViewModel,
    ) -> None:
        if not table.rows:
            return

        self._st.subheader(title)

        rows = [
            dict(
                zip(
                    table.columns,
                    row,
                    strict=True,
                )
            )
            for row in table.rows
        ]

        self._st.dataframe(
            rows,
            use_container_width=True,
            hide_index=True,
        )

    @staticmethod
    def _analytics_is_empty(
        analytics: AnalyticsSectionViewModel,
    ) -> bool:
        return (
            not analytics.metrics
            and not analytics.equity_curve.rows
            and not analytics.equity_curve_chart.points
            and not analytics.monthly_performance.rows
            and not analytics.monthly_performance_chart.points
            and not analytics.yearly_performance.rows
            and not analytics.yearly_performance_chart.points
            and not analytics.drawdown.rows
            and not analytics.drawdown_chart.points
            and not analytics.symbol_distribution.rows
            and not analytics.weekday_distribution.rows
        )


StreamlitRenderer = StreamlitDashboardRenderer