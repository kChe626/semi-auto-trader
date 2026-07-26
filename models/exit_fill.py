from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite


@dataclass(frozen=True, slots=True)
class ExitFill:
    """
    Broker-confirmed execution that closed a trade.
    """

    order_id: str
    filled_price: float
    filled_quantity: float
    filled_at: datetime

    def __post_init__(self) -> None:
        normalized_order_id = str(
            self.order_id
        ).strip()

        if not normalized_order_id:
            raise ValueError(
                "order_id cannot be empty"
            )

        try:
            normalized_price = float(
                self.filled_price
            )
        except (TypeError, ValueError) as error:
            raise ValueError(
                "filled_price must be a number"
            ) from error

        try:
            normalized_quantity = float(
                self.filled_quantity
            )
        except (TypeError, ValueError) as error:
            raise ValueError(
                "filled_quantity must be a number"
            ) from error

        if not isfinite(normalized_price):
            raise ValueError(
                "filled_price must be finite"
            )

        if not isfinite(normalized_quantity):
            raise ValueError(
                "filled_quantity must be finite"
            )

        if normalized_price <= 0:
            raise ValueError(
                "filled_price must be greater than zero"
            )

        if normalized_quantity <= 0:
            raise ValueError(
                "filled_quantity must be greater than zero"
            )

        if not isinstance(
            self.filled_at,
            datetime,
        ):
            raise ValueError(
                "filled_at must be a datetime"
            )

        if (
            self.filled_at.tzinfo is None
            or self.filled_at.utcoffset() is None
        ):
            raise ValueError(
                "filled_at must be timezone-aware"
            )

        object.__setattr__(
            self,
            "order_id",
            normalized_order_id,
        )

        object.__setattr__(
            self,
            "filled_price",
            normalized_price,
        )

        object.__setattr__(
            self,
            "filled_quantity",
            normalized_quantity,
        )