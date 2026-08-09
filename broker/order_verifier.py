from __future__ import annotations

from typing import Any

from alpaca.trading.client import TradingClient


def verify_submitted_order(
    client: TradingClient,
    order_id: Any,
):
    """
    Retrieve a submitted order from Alpaca by its order ID.

    Raises ValueError if the order ID is missing.
    Propagates Alpaca API errors to the caller.
    """
    if order_id is None:
        raise ValueError(
            "Cannot verify an order without an order ID."
        )

    return client.get_order_by_id(
        order_id
    )


class AlpacaOrderVerifier:
    """
    Adapter used by TradeExecutor to verify that a
    submitted Alpaca order can be retrieved.
    """

    def __init__(
        self,
        client: TradingClient,
    ) -> None:
        self._client = client

    def verify(
        self,
        order_id: str,
    ):
        return verify_submitted_order(
            client=self._client,
            order_id=order_id,
        )