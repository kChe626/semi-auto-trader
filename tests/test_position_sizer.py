import pytest

from risk.position_sizer import calculate_position_size


def test_calculate_position_size() -> None:
    quantity = calculate_position_size(
        account_equity=10_000.00,
        risk_percent=0.01,
        entry_price=100.00,
        stop_price=95.00,
    )

    assert quantity == 20


def test_position_size_rounds_down() -> None:
    quantity = calculate_position_size(
        account_equity=10_000.00,
        risk_percent=0.01,
        entry_price=100.00,
        stop_price=94.00,
    )

    assert quantity == 16


def test_rejects_zero_account_equity() -> None:
    with pytest.raises(
        ValueError,
        match="Account equity must be greater than zero",
    ):
        calculate_position_size(
            account_equity=0,
            risk_percent=0.01,
            entry_price=100.00,
            stop_price=95.00,
        )


def test_rejects_invalid_risk_percent() -> None:
    with pytest.raises(
        ValueError,
        match="Risk percent must be greater than zero",
    ):
        calculate_position_size(
            account_equity=10_000.00,
            risk_percent=0,
            entry_price=100.00,
            stop_price=95.00,
        )


def test_rejects_equal_entry_and_stop() -> None:
    with pytest.raises(
        ValueError,
        match="Entry price and stop price cannot be equal",
    ):
        calculate_position_size(
            account_equity=10_000.00,
            risk_percent=0.01,
            entry_price=100.00,
            stop_price=100.00,
        )