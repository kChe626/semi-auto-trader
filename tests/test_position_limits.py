from risk.position_limits import cap_position_size


def test_position_is_capped() -> None:
    quantity = cap_position_size(
        quantity=77,
        entry_price=646.01,
        account_equity=100_000,
        max_position_percent=0.10,
    )

    assert quantity == 15


def test_position_not_capped() -> None:
    quantity = cap_position_size(
        quantity=20,
        entry_price=100,
        account_equity=100_000,
        max_position_percent=0.10,
    )

    assert quantity == 20


def test_zero_quantity() -> None:
    quantity = cap_position_size(
        quantity=0,
        entry_price=100,
        account_equity=100_000,
        max_position_percent=0.10,
    )

    assert quantity == 0