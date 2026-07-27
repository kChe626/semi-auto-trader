from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class TradeStatus(StrEnum):
    SUBMITTED = "SUBMITTED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class Trade:
    trade_id: str
    symbol: str
    quantity: float
    status: TradeStatus
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

        try:
            normalized_status = TradeStatus(self.status)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "invalid trade status"
            ) from exc

        object.__setattr__(
            self,
            "status",
            normalized_status,
        )