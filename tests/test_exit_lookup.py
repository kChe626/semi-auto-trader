from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID

import pytest
from alpaca.trading.enums import OrderSide, OrderStatus

from broker.exit_lookup import BrokerExitLookup
from models.exit_fill import ExitFill


PARENT_ORDER_ID = (
    "11111111-1111-1111-1111-111111111111"
)

TARGET_ORDER_ID = (
    "22222222-2222-2222-2222-222222222222"
)

STOP_ORDER_ID = (
    "33333333-3333-3333-3333-333333333333"
)


class FakeTradingClient:
    def __init__(
        self,
        parent_order: object,
    ) -> None:
        self.parent_order = parent_order
        self.requested_order_id: str | None = None
        self.requested_nested: bool | None = None

    def get_order_by_id(
        self,
        order_id: str,
        *,
        nested: bool = False,
    ) -> object:
        self.requested_order_id = order_id
        self.requested_nested = nested

        return self.parent_order


def make_order(
    *,
    order_id: str,
    side: OrderSide,
    status: OrderStatus,
    filled_avg_price: str | None = None,
    filled_qty: str | None = None,
    filled_at: datetime | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=UUID(order_id),
        side=side,
        status=status,
        filled_avg_price=filled_avg_price,
        filled_qty=filled_qty,
        filled_at=filled_at,
    )


def make_parent(
    *legs: object,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=UUID(PARENT_ORDER_ID),
        legs=list(legs),
    )


def test_returns_filled_target_leg() -> None:
    filled_at = datetime(
        2026,
        7,
        20,
        18,
        30,
        tzinfo=timezone.utc,
    )

    target_leg = make_order(
        order_id=TARGET_ORDER_ID,
        side=OrderSide.SELL,
        status=OrderStatus.FILLED,
        filled_avg_price="210.25",
        filled_qty="10",
        filled_at=filled_at,
    )

    stop_leg = make_order(
        order_id=STOP_ORDER_ID,
        side=OrderSide.SELL,
        status=OrderStatus.CANCELED,
    )

    client = FakeTradingClient(
        make_parent(
            target_leg,
            stop_leg,
        )
    )

    lookup = BrokerExitLookup(client)

    result = lookup.get_completed_exit(
        PARENT_ORDER_ID
    )

    assert isinstance(result, ExitFill)
    assert result.order_id == TARGET_ORDER_ID
    assert result.filled_price == pytest.approx(
        210.25
    )
    assert result.filled_quantity == pytest.approx(
        10.0
    )
    assert result.filled_at == filled_at

    assert (
        client.requested_order_id
        == PARENT_ORDER_ID
    )
    assert client.requested_nested is True


def test_returns_filled_stop_leg() -> None:
    filled_at = datetime(
        2026,
        7,
        20,
        17,
        0,
        tzinfo=timezone.utc,
    )

    target_leg = make_order(
        order_id=TARGET_ORDER_ID,
        side=OrderSide.SELL,
        status=OrderStatus.CANCELED,
    )

    stop_leg = make_order(
        order_id=STOP_ORDER_ID,
        side=OrderSide.SELL,
        status=OrderStatus.FILLED,
        filled_avg_price="194.75",
        filled_qty="10",
        filled_at=filled_at,
    )

    client = FakeTradingClient(
        make_parent(
            target_leg,
            stop_leg,
        )
    )

    result = BrokerExitLookup(
        client
    ).get_completed_exit(
        PARENT_ORDER_ID
    )

    assert result is not None
    assert result.order_id == STOP_ORDER_ID
    assert result.filled_price == pytest.approx(
        194.75
    )


def test_returns_none_when_parent_has_no_legs() -> None:
    client = FakeTradingClient(
        SimpleNamespace(
            id=UUID(PARENT_ORDER_ID),
            legs=None,
        )
    )

    result = BrokerExitLookup(
        client
    ).get_completed_exit(
        PARENT_ORDER_ID
    )

    assert result is None


def test_returns_none_when_no_exit_leg_filled() -> None:
    target_leg = make_order(
        order_id=TARGET_ORDER_ID,
        side=OrderSide.SELL,
        status=OrderStatus.CANCELED,
    )

    stop_leg = make_order(
        order_id=STOP_ORDER_ID,
        side=OrderSide.SELL,
        status=OrderStatus.CANCELED,
    )

    client = FakeTradingClient(
        make_parent(
            target_leg,
            stop_leg,
        )
    )

    result = BrokerExitLookup(
        client
    ).get_completed_exit(
        PARENT_ORDER_ID
    )

    assert result is None


def test_buy_leg_is_not_treated_as_exit() -> None:
    entry_leg = make_order(
        order_id=TARGET_ORDER_ID,
        side=OrderSide.BUY,
        status=OrderStatus.FILLED,
        filled_avg_price="200",
        filled_qty="10",
        filled_at=datetime(
            2026,
            7,
            20,
            14,
            30,
            tzinfo=timezone.utc,
        ),
    )

    client = FakeTradingClient(
        make_parent(entry_leg)
    )

    result = BrokerExitLookup(
        client
    ).get_completed_exit(
        PARENT_ORDER_ID
    )

    assert result is None


def test_empty_order_id_is_rejected() -> None:
    client = FakeTradingClient(
        make_parent()
    )

    lookup = BrokerExitLookup(client)

    with pytest.raises(
        ValueError,
        match="order_id cannot be empty",
    ):
        lookup.get_completed_exit("   ")


def test_latest_filled_exit_leg_is_selected() -> None:
    earlier_leg = make_order(
        order_id=TARGET_ORDER_ID,
        side=OrderSide.SELL,
        status=OrderStatus.FILLED,
        filled_avg_price="205",
        filled_qty="5",
        filled_at=datetime(
            2026,
            7,
            20,
            17,
            0,
            tzinfo=timezone.utc,
        ),
    )

    later_leg = make_order(
        order_id=STOP_ORDER_ID,
        side=OrderSide.SELL,
        status=OrderStatus.FILLED,
        filled_avg_price="202",
        filled_qty="5",
        filled_at=datetime(
            2026,
            7,
            20,
            18,
            0,
            tzinfo=timezone.utc,
        ),
    )

    client = FakeTradingClient(
        make_parent(
            earlier_leg,
            later_leg,
        )
    )

    result = BrokerExitLookup(
        client
    ).get_completed_exit(
        PARENT_ORDER_ID
    )

    assert result is not None
    assert result.order_id == STOP_ORDER_ID
    assert result.filled_price == pytest.approx(
        202.0
    )