from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ChartPointViewModel:
    """
    One point on an analytics chart.
    """

    x: datetime
    y: float


@dataclass(frozen=True)
class AnalyticsChartViewModel:
    """
    Presentation model for a line chart.
    """

    title: str
    points: tuple[ChartPointViewModel, ...]

    @property
    def is_empty(self) -> bool:
        return not self.points