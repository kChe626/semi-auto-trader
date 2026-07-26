from __future__ import annotations

from dataclasses import dataclass

from dashboard.analytics_chart_models import (
    AnalyticsChartViewModel,
)


@dataclass(frozen=True, slots=True)
class AnalyticsMetricViewModel:
    """
    One display-ready performance metric.
    """

    label: str
    value: str


@dataclass(frozen=True, slots=True)
class AnalyticsTableViewModel:
    """
    Display-ready analytics table.

    Columns contain the table headers. Each row must
    contain one value for every column.
    """

    columns: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]

    @property
    def is_empty(self) -> bool:
        return not self.rows


@dataclass(frozen=True, slots=True)
class AnalyticsSectionViewModel:
    """
    Complete display-ready performance analytics section.

    This model contains formatted metrics and tables plus
    numeric chart data. It does not calculate analytics or
    access storage.
    """

    metrics: tuple[AnalyticsMetricViewModel, ...]

    equity_curve: AnalyticsTableViewModel
    equity_curve_chart: AnalyticsChartViewModel

    monthly_performance_chart: AnalyticsChartViewModel
    yearly_performance_chart: AnalyticsChartViewModel
    drawdown_chart: AnalyticsChartViewModel

    drawdown: AnalyticsTableViewModel
    monthly_performance: AnalyticsTableViewModel
    yearly_performance: AnalyticsTableViewModel
    symbol_distribution: AnalyticsTableViewModel
    weekday_distribution: AnalyticsTableViewModel