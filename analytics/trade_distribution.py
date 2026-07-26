from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from models.closed_trade import ClosedTrade


@dataclass(frozen=True, slots=True)
class TradeDistribution:
    """
    Performance statistics for one distribution group.
    """

    group: str
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


class TradeDistributionCalculator:
    """
    Calculates trade performance grouped by symbol
    or entry weekday.
    """

    @staticmethod
    def by_symbol(
        trades: Iterable[ClosedTrade],
    ) -> tuple[TradeDistribution, ...]:
        normalized_trades = list(trades)

        TradeDistributionCalculator._validate_trades(
            normalized_trades
        )

        grouped_trades: dict[
            str,
            list[ClosedTrade],
        ] = {}

        for trade in normalized_trades:
            grouped_trades.setdefault(
                trade.symbol,
                [],
            ).append(trade)

        return tuple(
            TradeDistributionCalculator._calculate_group(
                group=symbol,
                trades=symbol_trades,
            )
            for symbol, symbol_trades
            in sorted(grouped_trades.items())
        )

    @staticmethod
    def by_weekday(
        trades: Iterable[ClosedTrade],
    ) -> tuple[TradeDistribution, ...]:
        normalized_trades = list(trades)

        TradeDistributionCalculator._validate_trades(
            normalized_trades
        )

        grouped_trades: dict[
            int,
            list[ClosedTrade],
        ] = {}

        for trade in normalized_trades:
            weekday_number = (
                trade.opened_at.weekday()
            )

            grouped_trades.setdefault(
                weekday_number,
                [],
            ).append(trade)

        return tuple(
            TradeDistributionCalculator._calculate_group(
                group=TradeDistributionCalculator
                ._weekday_name(weekday_number),
                trades=weekday_trades,
            )
            for weekday_number, weekday_trades
            in sorted(grouped_trades.items())
        )

    @staticmethod
    def _calculate_group(
        *,
        group: str,
        trades: list[ClosedTrade],
    ) -> TradeDistribution:
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

        return TradeDistribution(
            group=group,
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

    @staticmethod
    def _weekday_name(
        weekday_number: int,
    ) -> str:
        weekday_names = (
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        )

        return weekday_names[
            weekday_number
        ]