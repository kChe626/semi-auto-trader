import pytest

from execution.order_status_mapper import (
    OrderStatusMapper,
)
from models.trade import TradeStatus


@pytest.mark.parametrize(
    ("broker_status", "expected_status"),
    [
        ("new", TradeStatus.SUBMITTED),
        ("accepted", TradeStatus.SUBMITTED),
        (
            "partially_filled",
            TradeStatus.PARTIALLY_FILLED,
        ),
        ("filled", TradeStatus.FILLED),
        ("canceled", TradeStatus.CANCELLED),
        ("cancelled", TradeStatus.CANCELLED),
        ("rejected", TradeStatus.REJECTED),
    ],
)
def test_map_status_returns_trade_status(
    broker_status: str,
    expected_status: TradeStatus,
) -> None:
    result = OrderStatusMapper.map_status(
        broker_status
    )

    assert result is expected_status


def test_map_status_is_case_insensitive() -> None:
    result = OrderStatusMapper.map_status(
        "PARTIALLY_FILLED"
    )

    assert result is TradeStatus.PARTIALLY_FILLED


def test_map_status_rejects_unknown_status() -> None:
    with pytest.raises(
        ValueError,
        match="Unsupported broker order status",
    ):
        OrderStatusMapper.map_status(
            "unknown_status"
        )


def test_map_status_rejects_missing_status() -> None:
    with pytest.raises(
        ValueError,
        match="Broker order status is required",
    ):
        OrderStatusMapper.map_status("")