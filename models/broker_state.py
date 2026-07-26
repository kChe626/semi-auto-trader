from __future__ import annotations

from dataclasses import dataclass
from typing import Any


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


@dataclass(frozen=True)
class AccountSnapshot:
    status: str
    equity: float
    cash: float
    buying_power: float
    trading_blocked: bool
    account_blocked: bool
    shorting_enabled: bool

    @classmethod
    def from_broker(cls, account: Any) -> "AccountSnapshot":
        return cls(
            status=str(
                getattr(account, "status", "")
            ),
            equity=float(
                getattr(account, "equity", 0)
            ),
            cash=float(
                getattr(account, "cash", 0)
            ),
            buying_power=float(
                getattr(account, "buying_power", 0)
            ),
            trading_blocked=bool(
                getattr(
                    account,
                    "trading_blocked",
                    False,
                )
            ),
            account_blocked=bool(
                getattr(
                    account,
                    "account_blocked",
                    False,
                )
            ),
            shorting_enabled=bool(
                getattr(
                    account,
                    "shorting_enabled",
                    False,
                )
            ),
        )


@dataclass(frozen=True)
class PositionSnapshot:
    symbol: str
    quantity: float
    side: str
    average_entry_price: float
    current_price: float | None
    market_value: float | None
    unrealized_profit_loss: float | None

    @classmethod
    def from_broker(
        cls,
        position: Any,
    ) -> "PositionSnapshot":
        return cls(
            symbol=str(
                getattr(position, "symbol", "")
            ).upper(),
            quantity=float(
                getattr(position, "qty", 0)
            ),
            side=str(
                getattr(position, "side", "")
            ),
            average_entry_price=float(
                getattr(
                    position,
                    "avg_entry_price",
                    0,
                )
            ),
            current_price=_optional_float(
                getattr(
                    position,
                    "current_price",
                    None,
                )
            ),
            market_value=_optional_float(
                getattr(
                    position,
                    "market_value",
                    None,
                )
            ),
            unrealized_profit_loss=(
                _optional_float(
                    getattr(
                        position,
                        "unrealized_pl",
                        None,
                    )
                )
            ),
        )


@dataclass(frozen=True)
class OrderSnapshot:
    order_id: str
    symbol: str
    status: str
    side: str
    quantity: float
    filled_quantity: float
    filled_average_price: float | None
    order_class: str
    submitted_at: Any | None
    filled_at: Any | None
    cancelled_at: Any | None

    @classmethod
    def from_broker(
        cls,
        order: Any,
    ) -> "OrderSnapshot":
        return cls(
            order_id=str(
                getattr(order, "id", "")
            ),
            symbol=str(
                getattr(order, "symbol", "")
            ).upper(),
            status=str(
                getattr(order, "status", "")
            ),
            side=str(
                getattr(order, "side", "")
            ),
            quantity=float(
                getattr(order, "qty", 0)
                or 0
            ),
            filled_quantity=float(
                getattr(
                    order,
                    "filled_qty",
                    0,
                )
                or 0
            ),
            filled_average_price=(
                _optional_float(
                    getattr(
                        order,
                        "filled_avg_price",
                        None,
                    )
                )
            ),
            order_class=str(
                getattr(
                    order,
                    "order_class",
                    "",
                )
            ),
            submitted_at=getattr(
                order,
                "submitted_at",
                None,
            ),
            filled_at=getattr(
                order,
                "filled_at",
                None,
            ),
            cancelled_at=getattr(
                order,
                "canceled_at",
                None,
            ),
        )