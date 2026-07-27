from __future__ import annotations

from models.trade import Trade, TradeStatus


class InMemoryTradeRepository:
    def __init__(self) -> None:
        self._trades: dict[str, Trade] = {}

    def save(
        self,
        trade: Trade,
    ) -> None:
        trade_id = trade.trade_id

        if trade_id in self._trades:
            raise ValueError(
                "trade already exists"
            )

        self._trades[trade_id] = trade

    def get(
        self,
        trade_id: str,
    ) -> Trade | None:
        if not isinstance(trade_id, str) or not trade_id.strip():
            raise ValueError(
                "trade_id is required"
            )

        return self._trades.get(trade_id)

    def get_all(
        self,
    ) -> tuple[Trade, ...]:
        return tuple(self._trades.values())

    def get_open(
        self,
    ) -> tuple[Trade, ...]:
        open_statuses = {
            TradeStatus.SUBMITTED,
            TradeStatus.PARTIALLY_FILLED,
            TradeStatus.FILLED,
        }

        return tuple(
            trade
            for trade in self._trades.values()
            if trade.status in open_statuses
        )

    def update(
        self,
        trade: Trade,
    ) -> None:
        trade_id = trade.trade_id

        if trade_id not in self._trades:
            raise ValueError(
                "trade does not exist"
            )

        self._trades[trade_id] = trade

    def remove(
        self,
        trade_id: str,
    ) -> None:
        if not isinstance(trade_id, str) or not trade_id.strip():
            raise ValueError(
                "trade_id is required"
            )

        if trade_id not in self._trades:
            raise ValueError(
                "trade does not exist"
            )

        del self._trades[trade_id]