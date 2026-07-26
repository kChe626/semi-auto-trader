from __future__ import annotations

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import QueryOrderStatus
from alpaca.trading.requests import GetOrdersRequest

from models.broker_state import (
    AccountSnapshot,
    OrderSnapshot,
    PositionSnapshot,
)


class PositionMonitor:
    """
    Read-only interface to current Alpaca broker state.
    """

    def __init__(
        self,
        trading_client: TradingClient,
    ) -> None:
        self._client = trading_client

    def get_account(self) -> AccountSnapshot:
        account = self._client.get_account()

        return AccountSnapshot.from_broker(
            account
        )

    def get_open_positions(
        self,
    ) -> list[PositionSnapshot]:
        positions = self._client.get_all_positions()

        return [
            PositionSnapshot.from_broker(position)
            for position in positions
        ]

    def get_open_orders(
        self,
    ) -> list[OrderSnapshot]:
        request = GetOrdersRequest(
            status=QueryOrderStatus.OPEN,
            nested=True,
        )

        orders = self._client.get_orders(
            filter=request
        )

        return [
            OrderSnapshot.from_broker(order)
            for order in orders
        ]

    def get_recent_orders(
        self,
        limit: int = 100,
    ) -> list[OrderSnapshot]:
        if limit <= 0:
            raise ValueError(
                "limit must be greater than zero"
            )

        if limit > 500:
            raise ValueError(
                "limit cannot exceed 500"
            )

        request = GetOrdersRequest(
            status=QueryOrderStatus.ALL,
            limit=limit,
            nested=True,
        )

        orders = self._client.get_orders(
            filter=request
        )

        return [
            OrderSnapshot.from_broker(order)
            for order in orders
        ]