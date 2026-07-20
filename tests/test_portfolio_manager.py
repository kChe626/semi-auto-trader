from unittest.mock import MagicMock

from risk.portfolio_manager import PortfolioManager


def test_portfolio_allows_trade() -> None:
    client = MagicMock()
    client.get_all_positions.return_value = []

    manager = PortfolioManager(client)

    allowed, reason = manager.can_open_new_trade()

    assert allowed is True
    assert reason == ""


def test_portfolio_blocks_when_limit_reached() -> None:
    client = MagicMock()

    client.get_all_positions.return_value = [
        MagicMock(),
    ]

    manager = PortfolioManager(client)

    allowed, reason = manager.can_open_new_trade()

    assert allowed is False
    assert "Maximum open trades" in reason