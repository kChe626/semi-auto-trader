from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable

from models.closed_trade import ClosedTrade


@dataclass(frozen=True, slots=True)
class YearlyPerformance:
    """
    Trading-performance statistics for one calendar year.
    """

    year: int
    trade_count: int
    winning_trades: int
    losing_trades: int
    breakeven_trades: int
    win_rate: float
    net_realized_pl: float
    gross_profit: float
    gross_loss: float
    average_trade: float
    average_winner: float
    average_loser: float
    profit_factor: float | None
    total_r_multiple: float
    average_r_multiple: float
    best_trade_pl: float
    worst_trade_pl: float

    @property
    def period(self) -> str:
        """
        Return the year as a string.
        """
        return str(self.year)


class YearlyPerformanceCalculator:
    """
    Groups completed trades by calendar year and
    calculates performance statistics for each year.
    """

    @staticmethod
    def calculate(
        trades: Iterable[ClosedTrade],
    ) -> tuple[YearlyPerformance, ...]:
        normalized_trades = list(trades)

        YearlyPerformanceCalculator._validate_trades(
            normalized_trades
        )

        grouped_trades: dict[
            int,
            list[ClosedTrade],
        ] = {}

        for trade in normalized_trades:
            grouped_trades.setdefault(
                trade.closed_at.year,
                [],
            ).append(trade)

        yearly_results = [
            YearlyPerformanceCalculator._calculate_year(
                year=year,
                trades=year_trades,
            )
            for year, year_trades
            in sorted(grouped_trades.items())
        ]

        return tuple(yearly_results)

    @staticmethod
    def _calculate_year(
        *,
        year: int,
        trades: list[ClosedTrade],
    ) -> YearlyPerformance:
        realized_results = [
            trade.realized_pl
            for trade in trades
        ]

        r_multiples = [
            trade.r_multiple
            for trade in trades
        ]

        winning_results = [
            realized_pl
            for realized_pl in realized_results
            if realized_pl > 0
        ]

        losing_results = [
            realized_pl
            for realized_pl in realized_results
            if realized_pl < 0
        ]

        breakeven_results = [
            realized_pl
            for realized_pl in realized_results
            if realized_pl == 0
        ]

        trade_count = len(trades)
        winning_trades = len(winning_results)
        losing_trades = len(losing_results)
        breakeven_trades = len(
            breakeven_results
        )

        net_realized_pl = sum(
            realized_results
        )

        gross_profit = sum(
            winning_results
        )

        gross_loss = sum(
            losing_results
        )

        win_rate = (
            winning_trades / trade_count
            if trade_count > 0
            else 0.0
        )

        average_trade = (
            net_realized_pl / trade_count
            if trade_count > 0
            else 0.0
        )

        average_winner = (
            gross_profit / winning_trades
            if winning_trades > 0
            else 0.0
        )

        average_loser = (
            gross_loss / losing_trades
            if losing_trades > 0
            else 0.0
        )

        if gross_loss < 0:
            profit_factor: float | None = (
                gross_profit / abs(gross_loss)
            )
        elif gross_profit > 0:
            profit_factor = None
        else:
            profit_factor = 0.0

        total_r_multiple = sum(
            r_multiples
        )

        average_r_multiple = (
            total_r_multiple / trade_count
            if trade_count > 0
            else 0.0
        )

        return YearlyPerformance(
            year=year,
            trade_count=trade_count,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            breakeven_trades=breakeven_trades,
            win_rate=win_rate,
            net_realized_pl=net_realized_pl,
            gross_profit=gross_profit,
            gross_loss=gross_loss,
            average_trade=average_trade,
            average_winner=average_winner,
            average_loser=average_loser,
            profit_factor=profit_factor,
            total_r_multiple=total_r_multiple,
            average_r_multiple=average_r_multiple,
            best_trade_pl=max(
                realized_results
            ),
            worst_trade_pl=min(
                realized_results
            ),
        )

    @staticmethod
    def _validate_trades(
        trades: list[ClosedTrade],
    ) -> None:
        for trade in trades:
            if not isinstance(
                trade,
                ClosedTrade,
            ):
                raise TypeError(
                    "all trades must be "
                    "ClosedTrade instances"
                )

            numeric_values = (
                trade.entry_price,
                trade.exit_price,
                trade.quantity,
                trade.realized_pl,
                trade.r_multiple,
                trade.holding_duration_seconds,
            )

            if not all(
                math.isfinite(value)
                for value in numeric_values
            ):
                raise ValueError(
                    "closed trade numeric values "
                    "must be finite"
                )