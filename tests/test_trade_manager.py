from unittest.mock import MagicMock

from trade_management.trade_manager import (
    TradeManager,
)


def test_start_cycle_runs_lifecycle_sync() -> None:
    lifecycle = MagicMock()

    manager = TradeManager(
        lifecycle
    )

    manager.start_cycle()

    lifecycle.synchronize.assert_called_once_with()