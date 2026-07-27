from __future__ import annotations

from models.trade import TradeStatus


class OrderStatusMapper:
    _STATUS_MAP = {
        "new": TradeStatus.SUBMITTED,
        "accepted": TradeStatus.SUBMITTED,
        "partially_filled": TradeStatus.PARTIALLY_FILLED,
        "filled": TradeStatus.FILLED,
        "canceled": TradeStatus.CANCELLED,
        "cancelled": TradeStatus.CANCELLED,
        "rejected": TradeStatus.REJECTED,
    }

    @classmethod
    def map_status(
        cls,
        broker_status: str,
    ) -> TradeStatus:
        if (
            not isinstance(broker_status, str)
            or not broker_status.strip()
        ):
            raise ValueError(
                "Broker order status is required"
            )

        normalized_status = (
            broker_status
            .strip()
            .lower()
        )

        try:
            return cls._STATUS_MAP[
                normalized_status
            ]
        except KeyError as exc:
            raise ValueError(
                "Unsupported broker order status: "
                f"{broker_status}"
            ) from exc