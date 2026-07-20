import pytest

from risk.daily_loss import (
    calculate_daily_loss_limit,
    calculate_daily_pnl,
    daily_loss_limit_reached,
)


def test_calculate_daily_profit() -> None:
    result = calculate_daily_pnl(
        current_equity=101_000.00,
        previous_equity=100_000.00,
    )

    assert result == 1_000.00


def test_calculate_daily_loss() -> None:
    result = calculate_daily_pnl(
        current_equity=98_500.00,
        previous_equity=100_000.00,
    )

    assert result == -1_500.00


def test_calculate_daily_loss_limit() -> None:
    result = calculate_daily_loss_limit(
        previous_equity=100_000.00,
        max_daily_loss_percent=0.02,
    )

    assert result == 2_000.00


def test_daily_loss_limit_not_reached() -> None:
    result = daily_loss_limit_reached(
        current_equity=98_500.00,
        previous_equity=100_000.00,
        max_daily_loss_percent=0.02,
    )

    assert result is False


def test_daily_loss_limit_reached() -> None:
    result = daily_loss_limit_reached(
        current_equity=98_000.00,
        previous_equity=100_000.00,
        max_daily_loss_percent=0.02,
    )

    assert result is True


def test_daily_loss_limit_exceeded() -> None:
    result = daily_loss_limit_reached(
        current_equity=97_500.00,
        previous_equity=100_000.00,
        max_daily_loss_percent=0.02,
    )

    assert result is True


def test_rejects_invalid_previous_equity() -> None:
    with pytest.raises(
        ValueError,
        match="Previous equity must be greater than zero",
    ):
        calculate_daily_loss_limit(
            previous_equity=0,
            max_daily_loss_percent=0.02,
        )


def test_rejects_invalid_loss_percent() -> None:
    with pytest.raises(
        ValueError,
        match="Maximum daily loss percent",
    ):
        calculate_daily_loss_limit(
            previous_equity=100_000.00,
            max_daily_loss_percent=1.00,
        )