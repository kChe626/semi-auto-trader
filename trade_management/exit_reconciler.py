from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Any

from database.trade_journal import TradeJournal
from models.broker_state import PositionSnapshot
from models.exit_fill import ExitFill
from trade_management.trade_analytics import (
    TradeAnalytics,
)


class ExitReconciler:
    """
    Detects tracked trades whose broker positions
    are no longer open.

    When an open journaled trade is missing from the
    broker's current positions, the reconciler optionally
    retrieves its confirmed broker exit fill and calculates
    closed-trade analytics.

    The same persistent trade_id and parent order_id remain
    attached to the position_closed journal event.
    """

    def __init__(
        self,
        journal: TradeJournal,
        exit_lookup: Any | None = None,
    ) -> None:
        self._journal = journal
        self._exit_lookup = exit_lookup

    def reconcile_closed_positions(
        self,
        open_positions: Iterable[PositionSnapshot],
    ) -> int:
        open_symbols = {
            position.symbol.strip().upper()
            for position in open_positions
            if position.symbol.strip()
        }

        tracked_open_trades = (
            self._journal.get_open_trade_events()
        )

        closed_count = 0

        for event in tracked_open_trades:
            symbol = self._normalize_symbol(
                event.get("symbol")
            )

            trade_id = event.get("trade_id")
            order_id = event.get("order_id")

            if not symbol or not trade_id:
                continue

            if symbol in open_symbols:
                continue

            exit_fill = self._get_exit_fill(
                order_id
            )

            if (
                self._exit_lookup is not None
                and exit_fill is None
            ):
                # The position disappeared, but the broker
                # has not yet returned a confirmed completed
                # exit order. Wait for a later reconciliation
                # instead of inventing an exit price.
                continue

            analytics = self._calculate_analytics(
                event=event,
                exit_fill=exit_fill,
            )

            self._journal.record_event(
                symbol=symbol,
                asset_type=(
                    event.get("asset_type")
                    or "stock"
                ),
                signal_type=event.get(
                    "signal_type"
                ),
                score=event.get("score"),
                entry_price=event.get(
                    "entry_price"
                ),
                stop_price=event.get(
                    "stop_price"
                ),
                target_price=event.get(
                    "target_price"
                ),
                quantity=event.get(
                    "quantity"
                ),
                total_risk=event.get(
                    "total_risk"
                ),
                risk_reward_ratio=event.get(
                    "risk_reward_ratio"
                ),
                exit_price=(
                    exit_fill.filled_price
                    if exit_fill is not None
                    else None
                ),
                exited_at=(
                    exit_fill.filled_at.isoformat()
                    if exit_fill is not None
                    else None
                ),
                realized_pl=(
                    analytics.realized_pl
                    if analytics is not None
                    else None
                ),
                r_multiple=(
                    analytics.r_multiple
                    if analytics is not None
                    else None
                ),
                holding_duration_seconds=(
                    analytics.holding_duration_seconds
                    if analytics is not None
                    else None
                ),
                status="position_closed",
                reason=self._build_close_reason(
                    exit_fill
                ),
                trade_id=trade_id,
                order_id=order_id,
            )

            closed_count += 1

        return closed_count

    def _get_exit_fill(
        self,
        order_id: Any | None,
    ) -> ExitFill | None:
        if self._exit_lookup is None:
            return None

        normalized_order_id = str(
            order_id or ""
        ).strip()

        if not normalized_order_id:
            return None

        return (
            self._exit_lookup.get_completed_exit(
                normalized_order_id
            )
        )

    @staticmethod
    def _calculate_analytics(
        *,
        event: dict[str, Any],
        exit_fill: ExitFill | None,
    ):
        if exit_fill is None:
            return None

        entry_price = event.get(
            "entry_price"
        )

        stop_price = event.get(
            "stop_price"
        )

        created_at = event.get(
            "created_at"
        )

        if (
            entry_price is None
            or stop_price is None
            or not created_at
        ):
            return None

        entry_time = (
            ExitReconciler._parse_datetime(
                created_at
            )
        )

        if entry_time is None:
            return None

        return TradeAnalytics.calculate(
            entry_price=float(entry_price),
            stop_price=float(stop_price),
            exit_price=(
                exit_fill.filled_price
            ),
            quantity=(
                exit_fill.filled_quantity
            ),
            entry_time=entry_time,
            exit_time=exit_fill.filled_at,
            total_risk=event.get(
                "total_risk"
            ),
        )

    @staticmethod
    def _parse_datetime(
        value: Any,
    ) -> datetime | None:
        if isinstance(value, datetime):
            parsed_value = value
        else:
            try:
                parsed_value = (
                    datetime.fromisoformat(
                        str(value)
                    )
                )
            except (TypeError, ValueError):
                return None

        if (
            parsed_value.tzinfo is None
            or parsed_value.utcoffset() is None
        ):
            return None

        return parsed_value

    @staticmethod
    def _normalize_symbol(
        value: Any,
    ) -> str:
        return str(
            value or ""
        ).strip().upper()

    @staticmethod
    def _build_close_reason(
        exit_fill: ExitFill | None,
    ) -> str:
        if exit_fill is None:
            return (
                "Tracked position no longer exists "
                "in broker open positions"
            )

        return (
            "Broker-confirmed exit fill detected; "
            f"exit_order_id={exit_fill.order_id}"
        )