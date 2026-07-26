from __future__ import annotations

from enum import Enum
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from dashboard.account_service import (
    AccountDashboardData,
    AccountService,
    AccountSummary,
    OpenPosition,
)


class FakeStatus(Enum):
    ACTIVE = "ACTIVE"


def make_account() -> SimpleNamespace:
    return SimpleNamespace(
        status=FakeStatus.ACTIVE,
        cash="95000.50",
        equity="101500.25",
        buying_power="380000.00",
        portfolio_value="101500.25",
        last_equity="100000.00",
        trading_blocked=False,
        account_blocked=False,
    )


def make_position(
    *,
    symbol: str = "AAPL",
) -> SimpleNamespace:
    return SimpleNamespace(
        symbol=symbol,
        side="long",
        qty="10",
        avg_entry_price="200.00",
        current_price="205.00",
        market_value="2050.00",
        cost_basis="2000.00",
        unrealized_pl="50.00",
        unrealized_plpc="0.025",
    )


def test_load_account_data_returns_snapshot() -> None:
    trading_client = Mock()

    trading_client.get_account.return_value = (
        make_account()
    )
    trading_client.get_all_positions.return_value = [
        make_position(),
    ]

    service = AccountService(trading_client)

    result = service.load_account_data()

    assert isinstance(
        result,
        AccountDashboardData,
    )
    assert isinstance(
        result.account,
        AccountSummary,
    )
    assert len(result.open_positions) == 1
    assert isinstance(
        result.open_positions[0],
        OpenPosition,
    )


def test_account_values_are_normalized() -> None:
    trading_client = Mock()

    trading_client.get_account.return_value = (
        make_account()
    )
    trading_client.get_all_positions.return_value = []

    service = AccountService(trading_client)

    result = service.load_account_data()

    assert result.account == AccountSummary(
        status="ACTIVE",
        cash=95000.50,
        equity=101500.25,
        buying_power=380000.00,
        portfolio_value=101500.25,
        last_equity=100000.00,
        trading_blocked=False,
        account_blocked=False,
    )


def test_open_position_values_are_normalized() -> None:
    trading_client = Mock()

    trading_client.get_account.return_value = (
        make_account()
    )
    trading_client.get_all_positions.return_value = [
        make_position(symbol=" aapl "),
    ]

    service = AccountService(trading_client)

    result = service.load_account_data()

    assert result.open_positions == (
        OpenPosition(
            symbol="AAPL",
            side="long",
            quantity=10.0,
            average_entry_price=200.0,
            current_price=205.0,
            market_value=2050.0,
            cost_basis=2000.0,
            unrealized_profit_loss=50.0,
            unrealized_profit_loss_percent=0.025,
        ),
    )


def test_empty_positions_returns_empty_tuple() -> None:
    trading_client = Mock()

    trading_client.get_account.return_value = (
        make_account()
    )
    trading_client.get_all_positions.return_value = []

    service = AccountService(trading_client)

    result = service.load_account_data()

    assert result.open_positions == ()


def test_broker_methods_are_called_once() -> None:
    trading_client = Mock()

    trading_client.get_account.return_value = (
        make_account()
    )
    trading_client.get_all_positions.return_value = []

    service = AccountService(trading_client)

    service.load_account_data()

    trading_client.get_account\
        .assert_called_once_with()

    trading_client.get_all_positions\
        .assert_called_once_with()


def test_position_generator_is_supported() -> None:
    trading_client = Mock()

    trading_client.get_account.return_value = (
        make_account()
    )
    trading_client.get_all_positions.return_value = (
        position
        for position in (
            make_position(symbol="AAPL"),
            make_position(symbol="MSFT"),
        )
    )

    service = AccountService(trading_client)

    result = service.load_account_data()

    assert [
        position.symbol
        for position in result.open_positions
    ] == [
        "AAPL",
        "MSFT",
    ]


def test_missing_optional_values_default_to_zero() -> None:
    trading_client = Mock()

    trading_client.get_account.return_value = (
        SimpleNamespace(
            status="ACTIVE",
        )
    )
    trading_client.get_all_positions.return_value = [
        SimpleNamespace(
            symbol="AAPL",
            side="long",
        ),
    ]

    service = AccountService(trading_client)

    result = service.load_account_data()

    assert result.account.cash == 0.0
    assert result.account.equity == 0.0
    assert result.account.buying_power == 0.0

    position = result.open_positions[0]

    assert position.quantity == 0.0
    assert position.market_value == 0.0
    assert position.unrealized_profit_loss == 0.0


def test_invalid_numeric_value_is_rejected() -> None:
    trading_client = Mock()

    account = make_account()
    account.cash = "not-a-number"

    trading_client.get_account.return_value = (
        account
    )
    trading_client.get_all_positions.return_value = []

    service = AccountService(trading_client)

    with pytest.raises(
        ValueError,
        match="convertible to float",
    ):
        service.load_account_data()


def test_broker_exception_is_not_hidden() -> None:
    trading_client = Mock()

    trading_client.get_account.side_effect = (
        RuntimeError("broker unavailable")
    )

    service = AccountService(trading_client)

    with pytest.raises(
        RuntimeError,
        match="broker unavailable",
    ):
        service.load_account_data()