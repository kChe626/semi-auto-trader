from types import SimpleNamespace
from unittest.mock import Mock
from uuid import UUID

from alpaca.trading.enums import (
    OrderSide,
    OrderStatus,
)

from trade_management.exit_policy import (
    ExitAction,
    ExitDecision,
)
from trade_management.position_management_service import (
    PositionManagementService,
)


PARENT_ORDER_ID = (
    "11111111-1111-1111-1111-111111111111"
)

TARGET_ORDER_ID = (
    "22222222-2222-2222-2222-222222222222"
)

STOP_ORDER_ID = (
    "33333333-3333-3333-3333-333333333333"
)


def make_leg(
    *,
    order_id: str,
    side: OrderSide = OrderSide.SELL,
    status: OrderStatus = OrderStatus.NEW,
    stop_price: str | None = None,
    limit_price: str | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=UUID(order_id),
        side=side,
        status=status,
        stop_price=stop_price,
        limit_price=limit_price,
    )


def make_parent(
    *legs: object,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=UUID(PARENT_ORDER_ID),
        legs=list(legs),
    )


def test_hold_does_not_modify_broker() -> None:
    client = Mock()
    journal = Mock()

    service = PositionManagementService(
        trading_client=client,
        journal=journal,
    )

    result = service.apply(
        symbol="AAPL",
        parent_order_id=PARENT_ORDER_ID,
        entry_price=100.0,
        decision=ExitDecision(
            action=ExitAction.HOLD,
            reason="Trend remains healthy.",
        ),
        trade_id="trade-123",
    )

    assert result is False

    client.get_order_by_id.assert_not_called()
    client.replace_order_by_id.assert_not_called()
    client.cancel_order_by_id.assert_not_called()
    client.close_position.assert_not_called()
    journal.record_event.assert_not_called()


def test_breakeven_replaces_active_stop_leg() -> None:
    stop_leg = make_leg(
        order_id=STOP_ORDER_ID,
        status=OrderStatus.NEW,
        stop_price="98.00",
    )

    target_leg = make_leg(
        order_id=TARGET_ORDER_ID,
        status=OrderStatus.NEW,
        limit_price="104.00",
    )

    client = Mock()
    client.get_order_by_id.return_value = (
        make_parent(
            target_leg,
            stop_leg,
        )
    )

    journal = Mock()

    service = PositionManagementService(
        trading_client=client,
        journal=journal,
    )

    result = service.apply(
        symbol="AAPL",
        parent_order_id=PARENT_ORDER_ID,
        entry_price=100.0,
        decision=ExitDecision(
            action=(
                ExitAction
                .MOVE_STOP_TO_BREAKEVEN
            ),
            reason="Price reached +1R.",
        ),
        trade_id="trade-123",
    )

    assert result is True

    client.get_order_by_id.assert_called_once_with(
        PARENT_ORDER_ID,
        nested=True,
    )

    client.replace_order_by_id.assert_called_once()

    order_id = (
        client
        .replace_order_by_id
        .call_args
        .args[0]
    )

    request = (
        client
        .replace_order_by_id
        .call_args
        .kwargs["order_data"]
    )

    assert str(order_id) == STOP_ORDER_ID
    assert request.stop_price == 100.0

    client.close_position.assert_not_called()


def test_breakeven_records_adjustment() -> None:
    stop_leg = make_leg(
        order_id=STOP_ORDER_ID,
        status=OrderStatus.NEW,
        stop_price="98.00",
    )

    client = Mock()
    client.get_order_by_id.return_value = (
        make_parent(stop_leg)
    )

    journal = Mock()

    service = PositionManagementService(
        trading_client=client,
        journal=journal,
    )

    service.apply(
        symbol="AAPL",
        parent_order_id=PARENT_ORDER_ID,
        entry_price=100.0,
        decision=ExitDecision(
            action=(
                ExitAction
                .MOVE_STOP_TO_BREAKEVEN
            ),
            reason="Price reached +1R.",
        ),
        trade_id="trade-123",
    )

    journal.record_event.assert_called_once_with(
        symbol="AAPL",
        status="stop_adjusted",
        reason=(
            "Stop moved to breakeven: "
            "Price reached +1R."
        ),
        trade_id="trade-123",
        order_id=PARENT_ORDER_ID,
        stop_price=100.0,
    )


def test_close_cancels_open_exit_legs_then_closes_position(
) -> None:
    stop_leg = make_leg(
        order_id=STOP_ORDER_ID,
        status=OrderStatus.NEW,
        stop_price="98.00",
    )

    target_leg = make_leg(
        order_id=TARGET_ORDER_ID,
        status=OrderStatus.NEW,
        limit_price="104.00",
    )

    client = Mock()
    client.get_order_by_id.return_value = (
        make_parent(
            target_leg,
            stop_leg,
        )
    )

    journal = Mock()

    service = PositionManagementService(
        trading_client=client,
        journal=journal,
    )

    result = service.apply(
        symbol="AAPL",
        parent_order_id=PARENT_ORDER_ID,
        entry_price=100.0,
        decision=ExitDecision(
            action=ExitAction.CLOSE,
            reason=(
                "Maximum holding period reached."
            ),
        ),
        trade_id="trade-123",
    )

    assert result is True

    cancelled_ids = {
        str(call.args[0])
        for call in (
            client
            .cancel_order_by_id
            .call_args_list
        )
    }

    assert cancelled_ids == {
        TARGET_ORDER_ID,
        STOP_ORDER_ID,
    }

    client.close_position.assert_called_once_with(
        "AAPL"
    )


def test_close_records_managed_exit_request() -> None:
    stop_leg = make_leg(
        order_id=STOP_ORDER_ID,
        status=OrderStatus.NEW,
    )

    client = Mock()
    client.get_order_by_id.return_value = (
        make_parent(stop_leg)
    )

    journal = Mock()

    service = PositionManagementService(
        trading_client=client,
        journal=journal,
    )

    service.apply(
        symbol="AAPL",
        parent_order_id=PARENT_ORDER_ID,
        entry_price=100.0,
        decision=ExitDecision(
            action=ExitAction.CLOSE,
            reason=(
                "Price closed below "
                "the short SMA."
            ),
        ),
        trade_id="trade-123",
    )

    journal.record_event.assert_called_once_with(
        symbol="AAPL",
        status="managed_exit_requested",
        reason=(
            "Price closed below "
            "the short SMA."
        ),
        trade_id="trade-123",
        order_id=PARENT_ORDER_ID,
    )


def test_breakeven_ignores_filled_or_cancelled_legs() -> None:
    filled_stop = make_leg(
        order_id=STOP_ORDER_ID,
        status=OrderStatus.FILLED,
        stop_price="98.00",
    )

    cancelled_target = make_leg(
        order_id=TARGET_ORDER_ID,
        status=OrderStatus.CANCELED,
        limit_price="104.00",
    )

    client = Mock()
    client.get_order_by_id.return_value = (
        make_parent(
            filled_stop,
            cancelled_target,
        )
    )

    journal = Mock()

    service = PositionManagementService(
        trading_client=client,
        journal=journal,
    )

    result = service.apply(
        symbol="AAPL",
        parent_order_id=PARENT_ORDER_ID,
        entry_price=100.0,
        decision=ExitDecision(
            action=(
                ExitAction
                .MOVE_STOP_TO_BREAKEVEN
            ),
            reason="Price reached +1R.",
        ),
        trade_id="trade-123",
    )

    assert result is False

    client.replace_order_by_id.assert_not_called()
    journal.record_event.assert_not_called()