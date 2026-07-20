import pytest

from risk.atr_price_levels import calculate_atr_price_levels


def test_buy_levels():
    stop, target = calculate_atr_price_levels(
        entry_price=100,
        atr=2,
        signal_type="BUY",
        atr_multiplier=2,
        reward_ratio=2,
    )

    assert stop == pytest.approx(96)
    assert target == pytest.approx(108)


def test_sell_levels():
    stop, target = calculate_atr_price_levels(
        entry_price=100,
        atr=2,
        signal_type="SELL",
        atr_multiplier=2,
        reward_ratio=2,
    )

    assert stop == pytest.approx(104)
    assert target == pytest.approx(92)


def test_rounds_to_cents():
    stop, target = calculate_atr_price_levels(
        entry_price=101.23,
        atr=1.37,
        signal_type="BUY",
        atr_multiplier=1.5,
        reward_ratio=2,
    )

    assert stop == round(stop, 2)
    assert target == round(target, 2)


def test_invalid_signal():
    with pytest.raises(ValueError):
        calculate_atr_price_levels(
            100,
            2,
            "INVALID",
        )


def test_zero_atr():
    with pytest.raises(ValueError):
        calculate_atr_price_levels(
            100,
            0,
            "BUY",
        )


def test_negative_multiplier():
    with pytest.raises(ValueError):
        calculate_atr_price_levels(
            100,
            2,
            "BUY",
            atr_multiplier=-1,
        )