from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

from database.trade_journal import TradeJournal
from models.broker_state import PositionSnapshot
from trade_management.exit_policy import (
    ExitAction,
    evaluate_exit,
)
from trade_management.position_management_metrics import (
    calculate_trading_days_held,
    get_latest_sma_values,
)
from trade_management.position_management_service import (
    PositionManagementService,
)


class PositionManagementCoordinator:
    """
    Coordinate active position management for one
    broker position.

    Responsibilities:
    - recover trade context from the journal
    - find the original position_open event
    - load historical market data
    - calculate holding duration and SMA values
    - evaluate the exit policy
    - suppress duplicate stop adjustments
    - apply the resulting broker action
    """

    def __init__(
        self,
        *,
        journal: TradeJournal,
        management_service: PositionManagementService,
        historical_loader: Callable[[str], Any],
    ) -> None:
        self._journal = journal
        self._management_service = (
            management_service
        )
        self._historical_loader = (
            historical_loader
        )

    def manage_position(
        self,
        position: PositionSnapshot,
    ) -> bool:
        symbol = str(
            position.symbol
        ).strip().upper()

        if not symbol:
            return False

        if position.current_price is None:
            return False

        latest = (
            self._journal
            .get_latest_event_by_symbol(
                symbol
            )
        )

        if latest is None:
            return False

        latest_status = str(
            latest.get(
                "status",
                "",
            )
        ).strip().lower()

        if latest_status == "managed_exit_requested":
            return False

        trade_id = str(
            latest.get(
                "trade_id",
                "",
            )
            or ""
        ).strip()

        if not trade_id:
            return False

        events = (
            self._journal
            .get_events_by_trade_id(
                trade_id
            )
        )

        open_event = self._find_position_open_event(
            events
        )

        if open_event is None:
            return False

        parent_order_id = str(
            open_event.get(
                "order_id",
                "",
            )
            or ""
        ).strip()

        if not parent_order_id:
            return False

        entry_price = open_event.get(
            "entry_price"
        )

        stop_price = open_event.get(
            "stop_price"
        )

        if (
            entry_price is None
            or stop_price is None
        ):
            return False

        opened_at_value = open_event.get(
            "created_at"
        )

        if not opened_at_value:
            return False

        opened_at = datetime.fromisoformat(
            str(opened_at_value)
        )

        historical_data = (
            self._historical_loader(
                symbol
            )
        )

        trading_days_held = (
            calculate_trading_days_held(
                historical_data,
                opened_at=opened_at,
            )
        )

        short_sma, long_sma = (
            get_latest_sma_values(
                historical_data
            )
        )

        decision = evaluate_exit(
            entry_price=float(
                entry_price
            ),
            initial_stop_price=float(
                stop_price
            ),
            current_price=float(
                position.current_price
            ),
            short_sma=short_sma,
            long_sma=long_sma,
            trading_days_held=(
                trading_days_held
            ),
        )

        already_adjusted = any(
            str(
                event.get(
                    "status",
                    "",
                )
            ).strip().lower()
            == "stop_adjusted"
            for event in events
        )

        if (
            decision.action
            == ExitAction.MOVE_STOP_TO_BREAKEVEN
            and already_adjusted
        ):
            return False

        return bool(
            self._management_service.apply(
                symbol=symbol,
                parent_order_id=(
                    parent_order_id
                ),
                entry_price=float(
                    entry_price
                ),
                decision=decision,
                trade_id=trade_id,
            )
        )

    @staticmethod
    def _find_position_open_event(
        events: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        position_open_events = [
            event
            for event in events
            if str(
                event.get(
                    "status",
                    "",
                )
            ).strip().lower()
            == "position_open"
        ]

        if not position_open_events:
            return None

        return position_open_events[0]