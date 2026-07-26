from datetime import datetime, timezone

from analytics.equity_curve import (
    EquityCurve,
    EquityCurvePoint,
)
from dashboard.analytics_chart_models import (
    AnalyticsChartViewModel,
    ChartPointViewModel,
)
from dashboard.analytics_presentation_mapper import (
    AnalyticsPresentationMapper,
)


CLOSED_AT = datetime(
    2026,
    7,
    26,
    17,
    0,
    tzinfo=timezone.utc,
)


def test_equity_curve_is_mapped_to_chart() -> None:
    mapper = AnalyticsPresentationMapper()

    equity_curve = EquityCurve(
        starting_equity=100_000.0,
        ending_equity=100_250.0,
        total_realized_pl=250.0,
        points=(
            EquityCurvePoint(
                trade_id="trade-1",
                symbol="AAPL",
                closed_at=CLOSED_AT,
                realized_pl=100.0,
                cumulative_pl=100.0,
                equity=100_100.0,
            ),
            EquityCurvePoint(
                trade_id="trade-2",
                symbol="MSFT",
                closed_at=CLOSED_AT,
                realized_pl=150.0,
                cumulative_pl=250.0,
                equity=100_250.0,
            ),
        ),
    )

    result = mapper.map_equity_curve_chart(
        equity_curve
    )

    assert result == AnalyticsChartViewModel(
        title="Equity Curve",
        points=(
            ChartPointViewModel(
                x=CLOSED_AT,
                y=100_100.0,
            ),
            ChartPointViewModel(
                x=CLOSED_AT,
                y=100_250.0,
            ),
        ),
    )


def test_empty_equity_curve_returns_empty_chart() -> None:
    mapper = AnalyticsPresentationMapper()

    equity_curve = EquityCurve(
        starting_equity=100_000.0,
        ending_equity=100_000.0,
        total_realized_pl=0.0,
        points=(),
    )

    result = mapper.map_equity_curve_chart(
        equity_curve
    )

    assert result.title == "Equity Curve"
    assert result.points == ()
    assert result.is_empty is True