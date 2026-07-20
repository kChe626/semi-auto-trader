
import pytest

from alpaca.trading.enums import (
    OrderClass,
    OrderSide,
    TimeInForce,
)

from broker.order_builder import build_bracket_order_request
from models.trade_plan import TradePlan


def create_buy_plan(
    quantity: int = 10,
) -> TradePlan:
    return TradePlan(
        symbol="META",
        signal_type="BUY",
        entry_price=100.00,
        stop_price=98.00,
        target_price=104.00,
        quantity=quantity,
        risk_per_share=2.00,
        reward_per_share=4.00,
        total_risk=quantity * 2.00,
        risk_reward_ratio=2.00,
    )


def create_sell_plan() -> TradePlan:
    return TradePlan(
        symbol="META",
        signal_type="SELL",
        entry_price=100.00,
        stop_price=102.00,
        target_price=96.00,
        quantity=10,
        risk_per_share=2.00,
        reward_per_share=4.00,
        total_risk=20.00,
        risk_reward_ratio=2.00,
    )


def test_build_buy_bracket_order() -> None:
    request = build_bracket_order_request(
        create_buy_plan()
    )

    assert request.symbol == "META"
    assert request.qty == 10
    assert request.side == OrderSide.BUY
    assert request.time_in_force == TimeInForce.DAY
    assert request.order_class == OrderClass.BRACKET
    assert request.take_profit is not None
    assert request.stop_loss is not None
    assert request.take_profit.limit_price == 104.00
    assert request.stop_loss.stop_price == 98.00


def test_build_sell_bracket_order() -> None:
    request = build_bracket_order_request(
        create_sell_plan()
    )

    assert request.side == OrderSide.SELL
    assert request.take_profit is not None
    assert request.stop_loss is not None
    assert request.take_profit.limit_price == 96.00
    assert request.stop_loss.stop_price == 102.00


def test_rejects_zero_quantity() -> None:
    with pytest.raises(
        ValueError,
        match="Order quantity must be greater than zero",
    ):
        build_bracket_order_request(
            create_buy_plan(quantity=0)
        )


def test_rejects_invalid_buy_stop() -> None:
    plan = create_buy_plan()
    plan.stop_price = 101.00

    with pytest.raises(
        ValueError,
        match="stop price must be below entry price",
    ):
        build_bracket_order_request(plan)


def test_rejects_invalid_buy_target() -> None:
    plan = create_buy_plan()
    plan.target_price = 99.00

    with pytest.raises(
        ValueError,
        match="target price must be above entry price",
    ):
        build_bracket_order_request(plan)