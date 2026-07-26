from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime

from models.closed_trade import ClosedTrade


@dataclass(frozen=True, slots=True)
class EquityCurvePoint:
    """
    Represents account equity immediately after
    one completed trade.
    """

    trade_id: str
    symbol: str
    closed_at: datetime
    realized_pl: float
    cumulative_pl: float
    equity: float


@dataclass(frozen=True, slots=True)
class EquityCurve:
    """
    Complete equity-curve result.
    """

    starting_equity: float
    ending_equity: float
    total_realized_pl: float
    points: tuple[EquityCurvePoint, ...]


class EquityCurveCalculator:
    """
    Builds a chronological equity curve from completed
    trades.

    The calculator has no database, broker, network,
    or file-system dependencies.
    """

    @staticmethod
    def calculate(
        trades: Iterable[ClosedTrade],
        *,
        starting_equity: float,
    ) -> EquityCurve:
        EquityCurveCalculator._validate_starting_equity(
            starting_equity
        )

        trade_list = sorted(
            trades,
            key=lambda trade: (
                trade.closed_at,
                trade.trade_id,
            ),
        )

        running_equity = float(starting_equity)
        cumulative_pl = 0.0
        points: list[EquityCurvePoint] = []

        for trade in trade_list:
            cumulative_pl += trade.realized_pl
            running_equity += trade.realized_pl

            points.append(
                EquityCurvePoint(
                    trade_id=trade.trade_id,
                    symbol=trade.symbol,
                    closed_at=trade.closed_at,
                    realized_pl=trade.realized_pl,
                    cumulative_pl=cumulative_pl,
                    equity=running_equity,
                )
            )

        return EquityCurve(
            starting_equity=float(starting_equity),
            ending_equity=running_equity,
            total_realized_pl=cumulative_pl,
            points=tuple(points),
        )

    @staticmethod
    def _validate_starting_equity(
        starting_equity: float,
    ) -> None:
        if not isinstance(
            starting_equity,
            (int, float),
        ):
            raise TypeError(
                "starting_equity must be numeric"
            )

        normalized_equity = float(
            starting_equity
        )

        if not math.isfinite(normalized_equity):
            raise ValueError(
                "starting_equity must be finite"
            )

        if normalized_equity <= 0:
            raise ValueError(
                "starting_equity must be greater than zero"
            )