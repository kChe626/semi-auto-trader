from __future__ import annotations

from typing import Any

from alpaca.trading.enums import (
    OrderSide,
    OrderStatus,
)
from alpaca.trading.requests import (
    ReplaceOrderRequest,
)

from database.trade_journal import TradeJournal
from trade_management.exit_policy import (
    ExitAction,
    ExitDecision,
)


class PositionManagementService:
    """
    Apply position-management decisions to a single
    Alpaca paper-trading position.

    This service never performs account-wide order
    cancellation or position liquidation.
    """

    _OPEN_STATUSES = {
        OrderStatus.NEW,
        OrderStatus.ACCEPTED,
        OrderStatus.PENDING_NEW,
        OrderStatus.PARTIALLY_FILLED,
    }

    def __init__(
        self,
        *,
        trading_client: Any,
        journal: TradeJournal,
    ) -> None:
        self._client = trading_client
        self._journal = journal

    def apply(
        self,
        *,
        symbol: str,
        parent_order_id: str,
        entry_price: float,
        decision: ExitDecision,
        trade_id: str,
    ) -> bool:
        normalized_symbol = str(
            symbol
        ).strip().upper()

        normalized_parent_order_id = str(
            parent_order_id
        ).strip()

        normalized_trade_id = str(
            trade_id
        ).strip()

        if not normalized_symbol:
            raise ValueError(
                "symbol is required"
            )

        if not normalized_parent_order_id:
            raise ValueError(
                "parent_order_id is required"
            )

        if not normalized_trade_id:
            raise ValueError(
                "trade_id is required"
            )

        if entry_price <= 0:
            raise ValueError(
                "entry_price must be greater than zero"
            )

        if decision.action == ExitAction.HOLD:
            return False

        if (
            decision.action
            == ExitAction.MOVE_STOP_TO_BREAKEVEN
        ):
            return self._move_stop_to_breakeven(
                symbol=normalized_symbol,
                parent_order_id=(
                    normalized_parent_order_id
                ),
                entry_price=entry_price,
                decision=decision,
                trade_id=normalized_trade_id,
            )

        if decision.action == ExitAction.CLOSE:
            return self._close_position(
                symbol=normalized_symbol,
                parent_order_id=(
                    normalized_parent_order_id
                ),
                decision=decision,
                trade_id=normalized_trade_id,
            )

        raise ValueError(
            f"Unsupported exit action: "
            f"{decision.action}"
        )

    def _move_stop_to_breakeven(
        self,
        *,
        symbol: str,
        parent_order_id: str,
        entry_price: float,
        decision: ExitDecision,
        trade_id: str,
    ) -> bool:
        parent_order = (
            self._client.get_order_by_id(
                parent_order_id,
                nested=True,
            )
        )

        stop_leg = self._find_active_stop_leg(
            parent_order
        )

        if stop_leg is None:
            return False

        stop_order_id = getattr(
            stop_leg,
            "id",
            None,
        )

        if stop_order_id is None:
            return False

        request = ReplaceOrderRequest(
            stop_price=round(
                entry_price,
                2,
            )
        )

        self._client.replace_order_by_id(
            stop_order_id,
            order_data=request,
        )

        self._journal.record_event(
            symbol=symbol,
            status="stop_adjusted",
            reason=(
                "Stop moved to breakeven: "
                f"{decision.reason}"
            ),
            trade_id=trade_id,
            order_id=parent_order_id,
            stop_price=round(
                entry_price,
                2,
            ),
        )

        return True

    def _close_position(
        self,
        *,
        symbol: str,
        parent_order_id: str,
        decision: ExitDecision,
        trade_id: str,
    ) -> bool:
        parent_order = (
            self._client.get_order_by_id(
                parent_order_id,
                nested=True,
            )
        )

        for leg in getattr(
            parent_order,
            "legs",
            None,
        ) or []:
            if not self._is_open_exit_leg(
                leg
            ):
                continue

            order_id = getattr(
                leg,
                "id",
                None,
            )

            if order_id is None:
                continue

            self._client.cancel_order_by_id(
                order_id
            )

        self._client.close_position(
            symbol
        )

        self._journal.record_event(
            symbol=symbol,
            status="managed_exit_requested",
            reason=decision.reason,
            trade_id=trade_id,
            order_id=parent_order_id,
        )

        return True

    def _find_active_stop_leg(
        self,
        parent_order: Any,
    ) -> Any | None:
        for leg in getattr(
            parent_order,
            "legs",
            None,
        ) or []:
            if not self._is_open_exit_leg(
                leg
            ):
                continue

            stop_price = getattr(
                leg,
                "stop_price",
                None,
            )

            if stop_price is None:
                continue

            return leg

        return None

    def _is_open_exit_leg(
        self,
        order: Any,
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

        return (
            side == OrderSide.SELL
            and status in self._OPEN_STATUSES
        )