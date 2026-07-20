from types import SimpleNamespace
from unittest.mock import MagicMock

from risk.portfolio_manager import PortfolioManager


def create_mock_client() -> MagicMock:
    client = MagicMock()

    client.get_all_positions.return_value = []
    client.get_orders.return_value = []

    client.get_account.return_value = SimpleNamespace(
        equity="100000.00",
        last_equity="100000.00",
    )

    return client


def test_portfolio_allows_trade() -> None:
    client = create_mock_client()

    manager = PortfolioManager(client)

    allowed, reason = manager.can_open_new_trade()

    assert allowed is True
    assert reason == ""


def test_portfolio_blocks_when_position_limit_reached() -> None:
    client = create_mock_client()

    client.get_all_positions.return_value = [
        SimpleNamespace(symbol="META"),
    ]

    manager = PortfolioManager(client)

    allowed, reason = manager.can_open_new_trade()

    assert allowed is False
    assert "Maximum active trades" in reason


def test_portfolio_blocks_when_open_order_exists() -> None:
    client = create_mock_client()

    client.get_orders.return_value = [
        SimpleNamespace(symbol="NVDA"),
    ]

    manager = PortfolioManager(client)

    allowed, reason = manager.can_open_new_trade()

    assert allowed is False
    assert "Maximum active trades" in reason


def test_position_and_orders_for_same_symbol_count_once() -> None:
    client = create_mock_client()

    client.get_all_positions.return_value = [
        SimpleNamespace(symbol="META"),
    ]

    client.get_orders.return_value = [
        SimpleNamespace(symbol="META"),
        SimpleNamespace(symbol="META"),
    ]

    manager = PortfolioManager(client)

    allowed, reason = manager.can_open_new_trade()

    assert allowed is False
    assert "Maximum active trades" in reason


def test_portfolio_blocks_when_daily_loss_limit_reached() -> None:
    client = create_mock_client()

    client.get_account.return_value = SimpleNamespace(
        equity="98000.00",
        last_equity="100000.00",
    )

    manager = PortfolioManager(client)

    allowed, reason = manager.can_open_new_trade()

    assert allowed is False
    assert "Daily loss limit reached" in reason
    assert "-$2,000.00" in reason


def test_portfolio_allows_trade_below_daily_loss_limit() -> None:
    client = create_mock_client()

    client.get_account.return_value = SimpleNamespace(
        equity="98500.00",
        last_equity="100000.00",
    )

    manager = PortfolioManager(client)

    allowed, reason = manager.can_open_new_trade()

    assert allowed is True
    assert reason == ""