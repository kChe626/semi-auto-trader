from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import datetime
from typing import Any, Protocol

from models.closed_trade import ClosedTrade


class ClosedTradeEventSource(Protocol):
    """
    Defines the journal method required by the repository.

    TradeJournal will implement this method in the next step.
    """

    def get_closed_trade_events(
        self,
    ) -> list[dict[str, Any]]:
        ...


class ClosedTradeRepository:
    """
    Converts completed journal events into validated
    ClosedTrade domain objects.

    The repository does not calculate performance
    statistics and does not communicate with the broker.
    """

    def __init__(
        self,
        event_source: ClosedTradeEventSource,
    ) -> None:
        self._event_source = event_source

    def get_all(self) -> list[ClosedTrade]:
        events = (
            self._event_source.get_closed_trade_events()
        )

        return self.from_events(events)

    @classmethod
    def from_events(
        cls,
        events: Iterable[Mapping[str, Any]],
    ) -> list[ClosedTrade]:
        return [
            cls._to_closed_trade(event)
            for event in events
        ]

    @staticmethod
    def _to_closed_trade(
        event: Mapping[str, Any],
    ) -> ClosedTrade:
        return ClosedTrade(
            trade_id=ClosedTradeRepository._require_text(
                event,
                "trade_id",
            ),
            symbol=ClosedTradeRepository._require_text(
                event,
                "symbol",
            ),
            entry_price=ClosedTradeRepository._require_float(
                event,
                "entry_price",
            ),
            exit_price=ClosedTradeRepository._require_float(
                event,
                "exit_price",
            ),
            quantity=ClosedTradeRepository._require_float(
                event,
                "quantity",
            ),
            realized_pl=ClosedTradeRepository._require_float(
                event,
                "realized_pl",
            ),
            r_multiple=ClosedTradeRepository._require_float(
                event,
                "r_multiple",
            ),
            holding_duration_seconds=(
                ClosedTradeRepository._require_float(
                    event,
                    "holding_duration_seconds",
                )
            ),
            opened_at=ClosedTradeRepository._require_datetime(
                event,
                "opened_at",
            ),
            closed_at=ClosedTradeRepository._require_datetime(
                event,
                "closed_at",
            ),
        )

    @staticmethod
    def _require_value(
        event: Mapping[str, Any],
        field_name: str,
    ) -> Any:
        if field_name not in event:
            raise ValueError(
                f"closed trade event is missing "
                f"{field_name}"
            )

        value = event[field_name]

        if value is None:
            raise ValueError(
                f"closed trade event has no "
                f"{field_name}"
            )

        return value

    @staticmethod
    def _require_text(
        event: Mapping[str, Any],
        field_name: str,
    ) -> str:
        value = ClosedTradeRepository._require_value(
            event,
            field_name,
        )

        normalized_value = str(value).strip()

        if not normalized_value:
            raise ValueError(
                f"closed trade event has empty "
                f"{field_name}"
            )

        return normalized_value

    @staticmethod
    def _require_float(
        event: Mapping[str, Any],
        field_name: str,
    ) -> float:
        value = ClosedTradeRepository._require_value(
            event,
            field_name,
        )

        try:
            return float(value)
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"closed trade event has invalid "
                f"{field_name}: {value!r}"
            ) from error

    @staticmethod
    def _require_datetime(
        event: Mapping[str, Any],
        field_name: str,
    ) -> datetime:
        value = ClosedTradeRepository._require_value(
            event,
            field_name,
        )

        if isinstance(value, datetime):
            return value

        if not isinstance(value, str):
            raise ValueError(
                f"closed trade event has invalid "
                f"{field_name}: {value!r}"
            )

        try:
            return datetime.fromisoformat(value)
        except ValueError as error:
            raise ValueError(
                f"closed trade event has invalid "
                f"{field_name}: {value!r}"
            ) from error