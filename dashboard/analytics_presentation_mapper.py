from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any, Iterable, Mapping

from dashboard.analytics_chart_models import (
    AnalyticsChartViewModel,
    ChartPointViewModel,
)
from dashboard.analytics_presentation_models import (
    AnalyticsMetricViewModel,
    AnalyticsSectionViewModel,
    AnalyticsTableViewModel,
)
from dashboard.dashboard_service import DashboardData


_MISSING = object()


class AnalyticsPresentationMapper:
    """
    Converts analytics-domain results into display-ready
    metrics, tables, and charts.

    The mapper performs formatting only. It does not
    calculate performance statistics or access storage.
    """

    _METRIC_DEFINITIONS = (
        (
            "Total Trades",
            ("total_trades", "trade_count"),
            "integer",
        ),
        (
            "Winning Trades",
            ("winning_trades", "win_count"),
            "integer",
        ),
        (
            "Losing Trades",
            ("losing_trades", "loss_count"),
            "integer",
        ),
        (
            "Win Rate",
            ("win_rate",),
            "percent",
        ),
        (
            "Net Profit/Loss",
            (
                "net_profit_loss",
                "total_profit_loss",
                "total_pnl",
                "net_pnl",
            ),
            "currency",
        ),
        (
            "Average Profit/Loss",
            (
                "average_profit_loss",
                "average_pnl",
                "avg_pnl",
            ),
            "currency",
        ),
        (
            "Average Win",
            ("average_win", "avg_win"),
            "currency",
        ),
        (
            "Average Loss",
            ("average_loss", "avg_loss"),
            "currency",
        ),
        (
            "Profit Factor",
            ("profit_factor",),
            "decimal",
        ),
        (
            "Expectancy",
            ("expectancy",),
            "currency",
        ),
    )

    def map_analytics_section(
        self,
        dashboard_data: DashboardData,
    ) -> AnalyticsSectionViewModel:
        return AnalyticsSectionViewModel(
            metrics=self._map_metrics(
                dashboard_data.performance_statistics
            ),
            equity_curve=self._map_table(
                dashboard_data.equity_curve
            ),
            equity_curve_chart=(
                self.map_equity_curve_chart(
                    dashboard_data.equity_curve
                )
            ),
            monthly_performance_chart=(
                self.map_monthly_performance_chart(
                    dashboard_data.monthly_performance
                )
            ),
            yearly_performance_chart=(
                self.map_yearly_performance_chart(
                    dashboard_data.yearly_performance
                )
            ),
            drawdown_chart=self.map_drawdown_chart(
                dashboard_data.drawdown
            ),
            drawdown=self._map_table(
                dashboard_data.drawdown
            ),
            monthly_performance=self._map_table(
                dashboard_data.monthly_performance
            ),
            yearly_performance=self._map_table(
                dashboard_data.yearly_performance
            ),
            symbol_distribution=self._map_table(
                dashboard_data.symbol_distribution
            ),
            weekday_distribution=self._map_table(
                dashboard_data.weekday_distribution
            ),
        )

    def map_equity_curve_chart(
        self,
        equity_curve: Any,
    ) -> AnalyticsChartViewModel:
        """
        Convert equity-curve points into numeric chart
        values.

        Unsupported or incomplete records are ignored.
        """

        raw_points = getattr(
            equity_curve,
            "points",
            equity_curve,
        )

        if raw_points is None:
            raw_points = ()

        chart_points: list[ChartPointViewModel] = []

        for point in raw_points:
            closed_at = self._find_value(
                point,
                ("closed_at",),
            )

            equity = self._find_value(
                point,
                ("equity",),
            )

            if (
                closed_at is _MISSING
                or equity is _MISSING
                or not isinstance(
                    closed_at,
                    datetime,
                )
            ):
                continue

            try:
                numeric_equity = float(equity)
            except (TypeError, ValueError):
                continue

            chart_points.append(
                ChartPointViewModel(
                    x=closed_at,
                    y=numeric_equity,
                )
            )

        return AnalyticsChartViewModel(
            title="Equity Curve",
            points=tuple(chart_points),
        )

    def map_monthly_performance_chart(
        self,
        monthly_performance: Any,
    ) -> AnalyticsChartViewModel:
        """
        Convert monthly-performance records into numeric
        chart values.

        Records without a month or realized profit/loss
        value are ignored.
        """

        raw_records = getattr(
            monthly_performance,
            "records",
            monthly_performance,
        )

        if raw_records is None:
            raw_records = ()

        chart_points: list[ChartPointViewModel] = []

        for record in raw_records:
            month = self._find_value(
                record,
                ("month",),
            )

            realized_profit_loss = self._find_value(
                record,
                (
                    "realized_profit_loss",
                    "net_profit_loss",
                    "total_profit_loss",
                    "total_pnl",
                    "net_pnl",
                ),
            )

            if (
                month is _MISSING
                or realized_profit_loss is _MISSING
            ):
                continue

            try:
                numeric_profit_loss = float(
                    realized_profit_loss
                )
            except (TypeError, ValueError):
                continue

            chart_points.append(
                ChartPointViewModel(
                    x=str(month),
                    y=numeric_profit_loss,
                )
            )

        return AnalyticsChartViewModel(
            title="Monthly Performance",
            points=tuple(chart_points),
        )

    def map_yearly_performance_chart(
        self,
        yearly_performance: Any,
    ) -> AnalyticsChartViewModel:
        """
        Convert yearly-performance records into numeric
        chart values.

        Records without a year or realized profit/loss
        value are ignored.
        """

        raw_records = getattr(
            yearly_performance,
            "records",
            yearly_performance,
        )

        if raw_records is None:
            raw_records = ()

        chart_points: list[ChartPointViewModel] = []

        for record in raw_records:
            year = self._find_value(
                record,
                ("year",),
            )

            realized_profit_loss = self._find_value(
                record,
                (
                    "realized_profit_loss",
                    "net_profit_loss",
                    "total_profit_loss",
                    "total_pnl",
                    "net_pnl",
                ),
            )

            if (
                year is _MISSING
                or realized_profit_loss is _MISSING
            ):
                continue

            try:
                numeric_profit_loss = float(
                    realized_profit_loss
                )
            except (TypeError, ValueError):
                continue

            chart_points.append(
                ChartPointViewModel(
                    x=str(year),
                    y=numeric_profit_loss,
                )
            )

        return AnalyticsChartViewModel(
            title="Yearly Performance",
            points=tuple(chart_points),
        )

    def map_drawdown_chart(
        self,
        drawdown: Any,
    ) -> AnalyticsChartViewModel:
        """
        Convert drawdown records into numeric chart values.

        DrawdownResult objects expose point data through
        the points attribute. Legacy records containers
        and direct iterables remain supported.
        """

        raw_records = getattr(
            drawdown,
            "points",
            _MISSING,
        )

        if raw_records is _MISSING:
            raw_records = getattr(
                drawdown,
                "records",
                drawdown,
            )

        if raw_records is None:
            raw_records = ()

        chart_points: list[ChartPointViewModel] = []

        for record in raw_records:
            drawdown_axis = self._find_value(
                record,
                (
                    "date",
                    "trade_id",
                ),
            )

            drawdown_value = self._find_value(
                record,
                (
                    "drawdown",
                    "drawdown_amount",
                ),
            )

            if (
                drawdown_axis is _MISSING
                or drawdown_value is _MISSING
                or not isinstance(
                    drawdown_axis,
                    (str, date, datetime),
                )
            ):
                continue

            try:
                numeric_drawdown = float(
                    drawdown_value
                )
            except (TypeError, ValueError):
                continue

            chart_points.append(
                ChartPointViewModel(
                    x=drawdown_axis,
                    y=numeric_drawdown,
                )
            )

        return AnalyticsChartViewModel(
            title="Drawdown",
            points=tuple(chart_points),
        )

    def _map_metrics(
        self,
        statistics: Any,
    ) -> tuple[AnalyticsMetricViewModel, ...]:
        metrics: list[AnalyticsMetricViewModel] = []

        for (
            label,
            aliases,
            format_type,
        ) in self._METRIC_DEFINITIONS:
            value = self._find_value(
                statistics,
                aliases,
            )

            if value is _MISSING:
                continue

            metrics.append(
                AnalyticsMetricViewModel(
                    label=label,
                    value=self._format_metric(
                        value,
                        format_type,
                    ),
                )
            )

        return tuple(metrics)

    def _map_table(
        self,
        value: Any,
    ) -> AnalyticsTableViewModel:
        records = tuple(
            self._extract_records(value)
        )

        if not records:
            return AnalyticsTableViewModel(
                columns=(),
                rows=(),
            )

        normalized_records = tuple(
            self._to_mapping(record)
            for record in records
        )

        columns = self._collect_columns(
            normalized_records
        )

        rows = tuple(
            tuple(
                self._format_table_value(
                    record.get(column)
                )
                for column in columns
            )
            for record in normalized_records
        )

        return AnalyticsTableViewModel(
            columns=tuple(
                self._format_column_name(column)
                for column in columns
            ),
            rows=rows,
        )

    def _extract_records(
        self,
        value: Any,
    ) -> Iterable[Any]:
        if value is None:
            return ()

        if isinstance(value, Mapping):
            return (value,)

        if isinstance(value, (str, bytes)):
            return ({"value": value},)

        for attribute_name in (
            "records",
            "results",
            "points",
            "rows",
            "data",
        ):
            nested_value = getattr(
                value,
                attribute_name,
                _MISSING,
            )

            if nested_value is not _MISSING:
                return self._extract_records(
                    nested_value
                )

        if isinstance(value, Iterable):
            return value

        return (value,)

    @staticmethod
    def _collect_columns(
        records: tuple[Mapping[str, Any], ...],
    ) -> tuple[str, ...]:
        columns: list[str] = []

        for record in records:
            for key in record:
                if key not in columns:
                    columns.append(key)

        return tuple(columns)

    def _to_mapping(
        self,
        value: Any,
    ) -> Mapping[str, Any]:
        if isinstance(value, Mapping):
            return {
                str(key): item
                for key, item in value.items()
            }

        if is_dataclass(value):
            return asdict(value)

        if hasattr(value, "_asdict"):
            return {
                str(key): item
                for key, item
                in value._asdict().items()
            }

        if hasattr(value, "__dict__"):
            return {
                key: item
                for key, item in vars(value).items()
                if not key.startswith("_")
            }

        return {"value": value}

    def _find_value(
        self,
        source: Any,
        aliases: tuple[str, ...],
    ) -> Any:
        if isinstance(source, Mapping):
            for alias in aliases:
                if alias in source:
                    return source[alias]

            return _MISSING

        for alias in aliases:
            if hasattr(source, alias):
                return getattr(source, alias)

        return _MISSING

    def _format_metric(
        self,
        value: Any,
        format_type: str,
    ) -> str:
        if value is None:
            return "N/A"

        if format_type == "integer":
            return f"{int(value):,}"

        if format_type == "currency":
            return self._format_currency(
                float(value)
            )

        if format_type == "percent":
            return self._format_percent(
                float(value)
            )

        if format_type == "decimal":
            return f"{float(value):.2f}"

        return str(value)

    @staticmethod
    def _format_currency(
        value: float,
    ) -> str:
        if value < 0:
            return f"-${abs(value):,.2f}"

        return f"${value:,.2f}"

    @staticmethod
    def _format_percent(
        value: float,
    ) -> str:
        normalized_value = (
            value / 100.0
            if abs(value) > 1.0
            else value
        )

        return f"{normalized_value:.2%}"

    def _format_table_value(
        self,
        value: Any,
    ) -> str:
        if value is None:
            return ""

        if isinstance(value, Enum):
            return str(value.value)

        if isinstance(value, datetime):
            return value.strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        if isinstance(value, date):
            return value.strftime(
                "%Y-%m-%d"
            )

        if isinstance(value, float):
            return f"{value:,.2f}"

        return str(value)

    @staticmethod
    def _format_column_name(
        value: str,
    ) -> str:
        return value.replace(
            "_",
            " ",
        ).title()