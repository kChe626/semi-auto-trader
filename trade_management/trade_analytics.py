from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite


@dataclass(frozen=True, slots=True)
class TradeResult:
    """
    Calculated results for one completed long trade.
    """

    realized_pl: float
    r_multiple: float
    holding_duration_seconds: float


class TradeAnalytics:
    """
    Pure calculation service for completed trades.

    This class does not communicate with the broker or
    database. It only validates inputs and calculates the
    realized performance of a completed long trade.
    """

    @staticmethod
    def calculate(
        *,
        entry_price: float,
        stop_price: float,
        exit_price: float,
        quantity: float,
        entry_time: datetime,
        exit_time: datetime,
        total_risk: float | None = None,
    ) -> TradeResult:
        normalized_entry_price = (
            TradeAnalytics._require_positive_number(
                entry_price,
                "entry_price",
            )
        )

        normalized_stop_price = (
            TradeAnalytics._require_positive_number(
                stop_price,
                "stop_price",
            )
        )

        normalized_exit_price = (
            TradeAnalytics._require_positive_number(
                exit_price,
                "exit_price",
            )
        )

        normalized_quantity = (
            TradeAnalytics._require_positive_number(
                quantity,
                "quantity",
            )
        )

        TradeAnalytics._validate_datetime(
            entry_time,
            "entry_time",
        )

        TradeAnalytics._validate_datetime(
            exit_time,
            "exit_time",
        )

        if exit_time < entry_time:
            raise ValueError(
                "exit_time cannot be earlier than entry_time"
            )

        if normalized_stop_price >= normalized_entry_price:
            raise ValueError(
                "stop_price must be below entry_price "
                "for a long trade"
            )

        if total_risk is None:
            calculated_total_risk = (
                normalized_entry_price
                - normalized_stop_price
            ) * normalized_quantity
        else:
            calculated_total_risk = (
                TradeAnalytics._require_positive_number(
                    total_risk,
                    "total_risk",
                )
            )

        realized_pl = (
            normalized_exit_price
            - normalized_entry_price
        ) * normalized_quantity

        r_multiple = (
            realized_pl
            / calculated_total_risk
        )

        holding_duration_seconds = (
            exit_time
            - entry_time
        ).total_seconds()

        return TradeResult(
            realized_pl=realized_pl,
            r_multiple=r_multiple,
            holding_duration_seconds=(
                holding_duration_seconds
            ),
        )

    @staticmethod
    def _require_positive_number(
        value: float,
        field_name: str,
    ) -> float:
        try:
            normalized_value = float(value)
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"{field_name} must be a number"
            ) from error

        if not isfinite(normalized_value):
            raise ValueError(
                f"{field_name} must be finite"
            )

        if normalized_value <= 0:
            raise ValueError(
                f"{field_name} must be greater than zero"
            )

        return normalized_value

    @staticmethod
    def _validate_datetime(
        value: datetime,
        field_name: str,
    ) -> None:
        if not isinstance(value, datetime):
            raise ValueError(
                f"{field_name} must be a datetime"
            )

        if value.tzinfo is None:
            raise ValueError(
                f"{field_name} must be timezone-aware"
            )

        if value.utcoffset() is None:
            raise ValueError(
                f"{field_name} must be timezone-aware"
            )