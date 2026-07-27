from __future__ import annotations

from dataclasses import replace
from typing import Any, Protocol

from execution.order_status_mapper import (
    OrderStatusMapper,
)
from models.trade import Trade


class BrokerProtocol(Protocol):
    def get_order_by_id(
        self,
        order_id: str,
    ) -> Any:
        ...


class TradeRepositoryProtocol(Protocol):
    def update(
        self,
        trade: Trade,
    ) -> None:
        ...

    def get_open(
        self,
    ) -> list[Trade]:
        ...


class OrderLifecycleService:
    def __init__(
        self,
        *,
        broker: BrokerProtocol,
        repository: TradeRepositoryProtocol,
    ) -> None:
        self._broker = broker
        self._repository = repository

    def sync_trade(
        self,
        trade: Trade,
    ) -> Trade:
        if not trade.parent_order_id:
            raise ValueError(
                "Parent order ID is required"
            )

        broker_order = self._broker.get_order_by_id(
            trade.parent_order_id
        )

        if broker_order is None:
            raise ValueError(
                "Broker order was not found"
            )

        updated_status = (
            OrderStatusMapper.map_status(
                broker_order.status
            )
        )

        if updated_status is trade.status:
            return trade

        updated_trade = replace(
            trade,
            status=updated_status,
        )

        self._repository.update(
            updated_trade
        )

        return updated_trade

    def sync_open_trades(
        self,
    ) -> list[Trade]:
        open_trades = (
            self._repository.get_open()
        )

        return [
            self.sync_trade(trade)
            for trade in open_trades
        ]