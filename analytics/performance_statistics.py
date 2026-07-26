from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from models.closed_trade import ClosedTrade


@dataclass(frozen=True, slots=True)
class PerformanceSummary:
    total_trades: int
    winners: int
    losers: int
    breakeven: int

    win_rate: float
    loss_rate: float
    breakeven_rate: float

    total_realized_pl: float
    average_realized_pl: float

    average_winner: float
    average_loser: float

    largest_winner: float
    largest_loser: float

    total_r: float
    average_r: float

    average_holding_duration_seconds: float
    expectancy: float


class PerformanceStatistics:
    """
    Calculates aggregate performance statistics
    from completed trades.

    This module contains no broker, database,
    network, or file-system dependencies.
    """

    @staticmethod
    def calculate(
        trades: Iterable[ClosedTrade],
    ) -> PerformanceSummary:
        trade_list = list(trades)

        if not trade_list:
            return PerformanceStatistics._empty_summary()

        winning_trades = [
            trade
            for trade in trade_list
            if trade.realized_pl > 0
        ]

        losing_trades = [
            trade
            for trade in trade_list
            if trade.realized_pl < 0
        ]

        breakeven_trades = [
            trade
            for trade in trade_list
            if trade.realized_pl == 0
        ]

        total_trades = len(trade_list)
        winners = len(winning_trades)
        losers = len(losing_trades)
        breakeven = len(breakeven_trades)

        realized_values = [
            trade.realized_pl
            for trade in trade_list
        ]

        r_values = [
            trade.r_multiple
            for trade in trade_list
        ]

        holding_durations = [
            trade.holding_duration_seconds
            for trade in trade_list
        ]

        winner_values = [
            trade.realized_pl
            for trade in winning_trades
        ]

        loser_values = [
            trade.realized_pl
            for trade in losing_trades
        ]

        total_realized_pl = sum(realized_values)
        total_r = sum(r_values)

        average_realized_pl = (
            total_realized_pl / total_trades
        )

        average_r = (
            total_r / total_trades
        )

        average_holding_duration_seconds = (
            sum(holding_durations) / total_trades
        )

        average_winner = (
            sum(winner_values) / winners
            if winners
            else 0.0
        )

        average_loser = (
            sum(loser_values) / losers
            if losers
            else 0.0
        )

        largest_winner = (
            max(winner_values)
            if winner_values
            else 0.0
        )

        largest_loser = (
            min(loser_values)
            if loser_values
            else 0.0
        )

        return PerformanceSummary(
            total_trades=total_trades,
            winners=winners,
            losers=losers,
            breakeven=breakeven,
            win_rate=(
                winners / total_trades * 100.0
            ),
            loss_rate=(
                losers / total_trades * 100.0
            ),
            breakeven_rate=(
                breakeven / total_trades * 100.0
            ),
            total_realized_pl=total_realized_pl,
            average_realized_pl=average_realized_pl,
            average_winner=average_winner,
            average_loser=average_loser,
            largest_winner=largest_winner,
            largest_loser=largest_loser,
            total_r=total_r,
            average_r=average_r,
            average_holding_duration_seconds=(
                average_holding_duration_seconds
            ),
            expectancy=average_realized_pl,
        )

    @staticmethod
    def _empty_summary() -> PerformanceSummary:
        return PerformanceSummary(
            total_trades=0,
            winners=0,
            losers=0,
            breakeven=0,
            win_rate=0.0,
            loss_rate=0.0,
            breakeven_rate=0.0,
            total_realized_pl=0.0,
            average_realized_pl=0.0,
            average_winner=0.0,
            average_loser=0.0,
            largest_winner=0.0,
            largest_loser=0.0,
            total_r=0.0,
            average_r=0.0,
            average_holding_duration_seconds=0.0,
            expectancy=0.0,
        )