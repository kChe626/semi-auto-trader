from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite


@dataclass(frozen=True, slots=True)
class ClosedTrade:
    trade_id: str
    symbol: str
    entry_price: float
    exit_price: float
    quantity: float
    realized_pl: float
    r_multiple: float
    holding_duration_seconds: float
    opened_at: datetime
    closed_at: datetime

    def __post_init__(self) -> None:
        trade_id = self.trade_id.strip()
        symbol = self.symbol.strip().upper()

        if not trade_id:
            raise ValueError(
                "trade_id cannot be empty"
            )

        if not symbol:
            raise ValueError(
                "symbol cannot be empty"
            )

        numeric_fields = {
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "quantity": self.quantity,
            "realized_pl": self.realized_pl,
            "r_multiple": self.r_multiple,
            "holding_duration_seconds": (
                self.holding_duration_seconds
            ),
        }

        for name, value in numeric_fields.items():
            if not isfinite(float(value)):
                raise ValueError(
                    f"{name} must be finite"
                )

        if self.entry_price <= 0:
            raise ValueError(
                "entry_price must be greater than zero"
            )

        if self.exit_price <= 0:
            raise ValueError(
                "exit_price must be greater than zero"
            )

        if self.quantity <= 0:
            raise ValueError(
                "quantity must be greater than zero"
            )

        if self.holding_duration_seconds < 0:
            raise ValueError(
                "holding_duration_seconds cannot be negative"
            )

        if (
            self.opened_at.tzinfo is None
            or self.opened_at.utcoffset() is None
        ):
            raise ValueError(
                "opened_at must be timezone-aware"
            )

        if (
            self.closed_at.tzinfo is None
            or self.closed_at.utcoffset() is None
        ):
            raise ValueError(
                "closed_at must be timezone-aware"
            )

        if self.closed_at < self.opened_at:
            raise ValueError(
                "closed_at cannot be before opened_at"
            )

        object.__setattr__(
            self,
            "trade_id",
            trade_id,
        )

        object.__setattr__(
            self,
            "symbol",
            symbol,
        )