from __future__ import annotations

from dataclasses import dataclass


_ALLOWED_STATUSES = {
    "SUBMITTED",
    "PARTIALLY_FILLED",
    "FILLED",
    "CLOSED",
    "CANCELLED",
    "REJECTED",
}


@dataclass(frozen=True)
class Trade:
    trade_id: str
    symbol: str
    quantity: float
    status: str
    entry_price: float
    stop_price: float
    target_price: float
    parent_order_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.trade_id, str) or not self.trade_id.strip():
            raise ValueError(
                "trade_id is required"
            )

        if not isinstance(self.symbol, str) or not self.symbol.strip():
            raise ValueError(
                "symbol is required"
            )

        if self.quantity <= 0:
            raise ValueError(
                "quantity must be greater than zero"
            )

        if self.entry_price <= 0:
            raise ValueError(
                "entry_price must be greater than zero"
            )

        if self.stop_price <= 0:
            raise ValueError(
                "stop_price must be greater than zero"
            )

        if self.target_price <= 0:
            raise ValueError(
                "target_price must be greater than zero"
            )

        if self.status not in _ALLOWED_STATUSES:
            raise ValueError(
                "invalid trade status"
            )