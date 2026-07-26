from __future__ import annotations

from collections.abc import Iterable

from analytics.performance_statistics import ClosedTrade
from dashboard.trade_history_presentation_models import (
    TradeHistoryRowViewModel,
    TradeHistorySectionViewModel,
)


class TradeHistoryPresentationMapper:
    """
    Convert closed trades into presentation-ready history rows.
    """

    def map(
        self,
        trades: Iterable[ClosedTrade],
    ) -> TradeHistorySectionViewModel:
        rows = tuple(
            self._map_trade(trade)
            for trade in trades
        )

        return TradeHistorySectionViewModel(
            rows=rows,
        )

    def _map_trade(
        self,
        trade: ClosedTrade,
    ) -> TradeHistoryRowViewModel:
        return TradeHistoryRowViewModel(
            trade_id=trade.trade_id,
            symbol=trade.symbol.upper(),
            side="LONG",
            opened_at=self._format_datetime(
                trade.opened_at
            ),
            closed_at=self._format_datetime(
                trade.closed_at
            ),
            quantity=self._format_quantity(
                trade.quantity
            ),
            entry_price=self._format_currency(
                trade.entry_price
            ),
            exit_price=self._format_currency(
                trade.exit_price
            ),
            realized_profit_loss=(
                self._format_currency(
                    trade.realized_pl
                )
            ),
            r_multiple=(
                f"{trade.r_multiple:.2f}R"
            ),
            holding_duration=(
                self._format_duration(
                    trade.holding_duration_seconds
                )
            ),
        )

    @staticmethod
    def _format_datetime(value) -> str:
        return value.strftime(
            "%Y-%m-%d %H:%M UTC"
        )

    @staticmethod
    def _format_quantity(
        quantity: float,
    ) -> str:
        if quantity.is_integer():
            return str(int(quantity))

        return (
            f"{quantity:.8f}"
            .rstrip("0")
            .rstrip(".")
        )

    @staticmethod
    def _format_currency(
        value: float,
    ) -> str:
        absolute_value = abs(value)
        formatted_value = (
            f"${absolute_value:,.2f}"
        )

        if value < 0:
            return f"-{formatted_value}"

        return formatted_value

    @staticmethod
    def _format_duration(
        seconds: float,
    ) -> str:
        total_seconds = int(seconds)

        days, remainder = divmod(
            total_seconds,
            86400,
        )
        hours, remainder = divmod(
            remainder,
            3600,
        )
        minutes, remaining_seconds = divmod(
            remainder,
            60,
        )

        parts: list[str] = []

        if days:
            parts.append(f"{days}d")

        if hours:
            parts.append(f"{hours}h")

        if minutes:
            parts.append(f"{minutes}m")

        if remaining_seconds or not parts:
            parts.append(
                f"{remaining_seconds}s"
            )

        return " ".join(parts)