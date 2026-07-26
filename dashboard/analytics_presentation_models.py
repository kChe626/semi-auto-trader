from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AnalyticsMetricViewModel:
    """
    One display-ready performance metric.
    """

    label: str
    value: str


@dataclass(frozen=True)
class AnalyticsTableViewModel:
    """
    Generic display-ready analytics table.
    """

    columns: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]

    @property
    def is_empty(self) -> bool:
        return not self.rows


@dataclass(frozen=True)
class AnalyticsSectionViewModel:
    """
    Complete presentation model for closed-trade
    analytics.
    """

    metrics: tuple[AnalyticsMetricViewModel, ...]
    equity_curve: AnalyticsTableViewModel
    drawdown: AnalyticsTableViewModel
    monthly_performance: AnalyticsTableViewModel
    yearly_performance: AnalyticsTableViewModel
    symbol_distribution: AnalyticsTableViewModel
    weekday_distribution: AnalyticsTableViewModel