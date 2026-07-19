import pytest

from risk.price_levels import calculate_price_levels


def test_calculate_buy_price_levels() -> None:
    stop_price, target_price = calculate_price_levels(
        signal_type="BUY",
        entry_price=100.00,
        stop_loss_percent=0.02,
        reward_risk_ratio=2.0,
    )

    assert stop_price == 98.00
    assert target_price == 104.00


def test_calculate_sell_price_levels() -> None:
    stop_price, target_price = calculate_price_levels(
        signal_type="SELL",
        entry_price=100.00,
        stop_loss_percent=0.02,
        reward_risk_ratio=2.0,
    )

    assert stop_price == 102.00
    assert target_price == 96.00


def test_price_levels_are_rounded_to_cents() -> None:
    stop_price, target_price = calculate_price_levels(
        signal_type="BUY",
        entry_price=123.45,
        stop_loss_percent=0.015,
        reward_risk_ratio=2.0,
    )

    assert stop_price == 121.60
    assert target_price == 127.15


def test_rejects_invalid_signal_type() -> None:
    with pytest.raises(
        ValueError,
        match="Signal type must be BUY or SELL",
    ):
        calculate_price_levels(
            signal_type="HOLD",
            entry_price=100.00,
        )


def test_rejects_invalid_stop_loss_percent() -> None:
    with pytest.raises(
        ValueError,
        match="Stop-loss percent must be greater than zero",
    ):
        calculate_price_levels(
            signal_type="BUY",
            entry_price=100.00,
            stop_loss_percent=0,
        )