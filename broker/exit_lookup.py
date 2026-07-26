from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Any

from alpaca.trading.enums import OrderSide, OrderStatus
from alpaca.trading.models import Order

from models.exit_fill import ExitFill


class BrokerExitLookup:
    """
    Retrieves the broker-confirmed closing fill for an
    Alpaca bracket order.

    The supplied order_id is expected to be the parent
    bracket order ID stored in the trade journal.
    """

    def __init__(
        self,
        trading_client: Any,
    ) -> None:
        self._trading_client = trading_client

    def get_completed_exit(
        self,
        order_id: str,
    ) -> ExitFill | None:
        normalized_order_id = str(
            order_id
        ).strip()

        if not normalized_order_id:
            raise ValueError(
                "order_id cannot be empty"
            )

        parent_order = (
            self._trading_client.get_order_by_id(
                normalized_order_id,
                nested=True,
            )
        )

        legs = getattr(
            parent_order,
            "legs",
            None,
        )

        if not legs:
            return None

        filled_exit_legs = [
            leg
            for leg in legs
            if self._is_completed_exit_leg(leg)
        ]

        if not filled_exit_legs:
            return None

        selected_leg = self._select_exit_leg(
            filled_exit_legs
        )

        return self._to_exit_fill(
            selected_leg
        )

    @staticmethod
    def _is_completed_exit_leg(
        order: Order,
    ) -> bool:
        side = getattr(
            order,
            "side",
            None,
        )

        status = getattr(
            order,
            "status",
            None,
        )

        filled_price = getattr(
            order,
            "filled_avg_price",
            None,
        )

        filled_quantity = getattr(
            order,
            "filled_qty",
            None,
        )

        filled_at = getattr(
            order,
            "filled_at",
            None,
        )

        return (
            side == OrderSide.SELL
            and status == OrderStatus.FILLED
            and filled_price is not None
            and filled_quantity is not None
            and filled_at is not None
        )

    @staticmethod
    def _select_exit_leg(
        orders: Iterable[Order],
    ) -> Order:
        """
        Select the most recently filled exit leg.

        A normal bracket order should have only one filled
        exit leg because Alpaca cancels the opposing leg.
        """
        return max(
            orders,
            key=lambda order: (
                getattr(
                    order,
                    "filled_at",
                    None,
                )
                or datetime.min
            ),
        )

    @staticmethod
    def _to_exit_fill(
        order: Order,
    ) -> ExitFill:
        order_id = getattr(
            order,
            "id",
            None,
        )

        filled_price = getattr(
            order,
            "filled_avg_price",
            None,
        )

        filled_quantity = getattr(
            order,
            "filled_qty",
            None,
        )

        filled_at = getattr(
            order,
            "filled_at",
            None,
        )

        if order_id is None:
            raise ValueError(
                "Filled exit order is missing id"
            )

        if filled_price is None:
            raise ValueError(
                "Filled exit order is missing "
                "filled_avg_price"
            )

        if filled_quantity is None:
            raise ValueError(
                "Filled exit order is missing filled_qty"
            )

        if filled_at is None:
            raise ValueError(
                "Filled exit order is missing filled_at"
            )

        return ExitFill(
            order_id=str(order_id),
            filled_price=float(filled_price),
            filled_quantity=float(
                filled_quantity
            ),
            filled_at=filled_at,
        )