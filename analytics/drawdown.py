from __future__ import annotations

import math
from dataclasses import dataclass

from analytics.equity_curve import (
    EquityCurve,
)


@dataclass(frozen=True, slots=True)
class DrawdownPoint:
    """
    Drawdown state after one completed trade.
    """

    trade_id: str
    symbol: str
    equity: float
    peak_equity: float
    drawdown_amount: float
    drawdown_percent: float


@dataclass(frozen=True, slots=True)
class DrawdownResult:
    """
    Summary and point-by-point drawdown statistics.
    """

    starting_equity: float
    ending_equity: float
    peak_equity: float
    current_drawdown_amount: float
    current_drawdown_percent: float
    maximum_drawdown_amount: float
    maximum_drawdown_percent: float
    maximum_drawdown_trade_id: str | None
    recovered: bool
    points: tuple[DrawdownPoint, ...]


class DrawdownCalculator:
    """
    Calculates running and maximum drawdown from an
    EquityCurve.
    """

    @staticmethod
    def calculate(
        curve: EquityCurve,
    ) -> DrawdownResult:
        DrawdownCalculator._validate_curve(
            curve
        )

        peak_equity = curve.starting_equity
        maximum_drawdown_amount = 0.0
        maximum_drawdown_percent = 0.0
        maximum_drawdown_trade_id: str | None = None

        points: list[DrawdownPoint] = []

        for equity_point in curve.points:
            equity = equity_point.equity

            if equity > peak_equity:
                peak_equity = equity

            drawdown_amount = (
                equity - peak_equity
            )

            drawdown_percent = (
                drawdown_amount / peak_equity
                if peak_equity > 0
                else 0.0
            )

            if (
                drawdown_amount
                < maximum_drawdown_amount
            ):
                maximum_drawdown_amount = (
                    drawdown_amount
                )

                maximum_drawdown_percent = (
                    drawdown_percent
                )

                maximum_drawdown_trade_id = (
                    equity_point.trade_id
                )

            points.append(
                DrawdownPoint(
                    trade_id=equity_point.trade_id,
                    symbol=equity_point.symbol,
                    equity=equity,
                    peak_equity=peak_equity,
                    drawdown_amount=(
                        drawdown_amount
                    ),
                    drawdown_percent=(
                        drawdown_percent
                    ),
                )
            )

        if points:
            current_drawdown_amount = (
                points[-1].drawdown_amount
            )

            current_drawdown_percent = (
                points[-1].drawdown_percent
            )
        else:
            current_drawdown_amount = 0.0
            current_drawdown_percent = 0.0

        recovered = (
            current_drawdown_amount == 0.0
        )

        return DrawdownResult(
            starting_equity=curve.starting_equity,
            ending_equity=curve.ending_equity,
            peak_equity=peak_equity,
            current_drawdown_amount=(
                current_drawdown_amount
            ),
            current_drawdown_percent=(
                current_drawdown_percent
            ),
            maximum_drawdown_amount=(
                maximum_drawdown_amount
            ),
            maximum_drawdown_percent=(
                maximum_drawdown_percent
            ),
            maximum_drawdown_trade_id=(
                maximum_drawdown_trade_id
            ),
            recovered=recovered,
            points=tuple(points),
        )

    @staticmethod
    def _validate_curve(
        curve: EquityCurve,
    ) -> None:
        if not isinstance(
            curve,
            EquityCurve,
        ):
            raise TypeError(
                "curve must be an EquityCurve"
            )

        values = (
            curve.starting_equity,
            curve.ending_equity,
            curve.total_realized_pl,
        )

        if not all(
            math.isfinite(value)
            for value in values
        ):
            raise ValueError(
                "equity curve values must be finite"
            )

        if curve.starting_equity <= 0:
            raise ValueError(
                "starting equity must be greater "
                "than zero"
            )

        for point in curve.points:
            point_values = (
                point.realized_pl,
                point.cumulative_pl,
                point.equity,
            )

            if not all(
                math.isfinite(value)
                for value in point_values
            ):
                raise ValueError(
                    "equity curve point values "
                    "must be finite"
                )