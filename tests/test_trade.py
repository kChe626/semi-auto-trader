import pytest

from models.trade import Trade


def test_trade_stores_submission_details() -> None:
    trade = Trade(
        trade_id="trade-123",
        symbol="AAPL",
        quantity=10,
        status="SUBMITTED",
        entry_price=200.00,
        stop_price=195.00,
        target_price=210.00,
        parent_order_id="order-456",
    )

    assert trade.trade_id == "trade-123"
    assert trade.symbol == "AAPL"
    assert trade.quantity == 10
    assert trade.status == "SUBMITTED"
    assert trade.entry_price == 200.00
    assert trade.stop_price == 195.00
    assert trade.target_price == 210.00
    assert trade.parent_order_id == "order-456"


def test_trade_rejects_empty_trade_id() -> None:
    with pytest.raises(
        ValueError,
        match="trade_id is required",
    ):
        Trade(
            trade_id="",
            symbol="AAPL",
            quantity=10,
            status="SUBMITTED",
            entry_price=200.00,
            stop_price=195.00,
            target_price=210.00,
            parent_order_id="order-456",
        )


def test_trade_rejects_empty_symbol() -> None:
    with pytest.raises(
        ValueError,
        match="symbol is required",
    ):
        Trade(
            trade_id="trade-123",
            symbol="",
            quantity=10,
            status="SUBMITTED",
            entry_price=200.00,
            stop_price=195.00,
            target_price=210.00,
            parent_order_id="order-456",
        )


@pytest.mark.parametrize(
    "quantity",
    [
        0,
        -1,
    ],
)
def test_trade_rejects_non_positive_quantity(
    quantity: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="quantity must be greater than zero",
    ):
        Trade(
            trade_id="trade-123",
            symbol="AAPL",
            quantity=quantity,
            status="SUBMITTED",
            entry_price=200.00,
            stop_price=195.00,
            target_price=210.00,
            parent_order_id="order-456",
        )


@pytest.mark.parametrize(
    "entry_price",
    [
        0,
        -1,
    ],
)
def test_trade_rejects_non_positive_entry_price(
    entry_price: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="entry_price must be greater than zero",
    ):
        Trade(
            trade_id="trade-123",
            symbol="AAPL",
            quantity=10,
            status="SUBMITTED",
            entry_price=entry_price,
            stop_price=195.00,
            target_price=210.00,
            parent_order_id="order-456",
        )


@pytest.mark.parametrize(
    "stop_price",
    [
        0,
        -1,
    ],
)
def test_trade_rejects_non_positive_stop_price(
    stop_price: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="stop_price must be greater than zero",
    ):
        Trade(
            trade_id="trade-123",
            symbol="AAPL",
            quantity=10,
            status="SUBMITTED",
            entry_price=200.00,
            stop_price=stop_price,
            target_price=210.00,
            parent_order_id="order-456",
        )


@pytest.mark.parametrize(
    "target_price",
    [
        0,
        -1,
    ],
)
def test_trade_rejects_non_positive_target_price(
    target_price: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="target_price must be greater than zero",
    ):
        Trade(
            trade_id="trade-123",
            symbol="AAPL",
            quantity=10,
            status="SUBMITTED",
            entry_price=200.00,
            stop_price=195.00,
            target_price=target_price,
            parent_order_id="order-456",
        )


def test_trade_rejects_invalid_status() -> None:
    with pytest.raises(
        ValueError,
        match="invalid trade status",
    ):
        Trade(
            trade_id="trade-123",
            symbol="AAPL",
            quantity=10,
            status="UNKNOWN",
            entry_price=200.00,
            stop_price=195.00,
            target_price=210.00,
            parent_order_id="order-456",
        )