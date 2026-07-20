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

    return client.get_order_by_id(order_id)