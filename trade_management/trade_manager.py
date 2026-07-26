from __future__ import annotations

from trade_management.lifecycle_engine import (
    TradeLifecycleEngine,
)


class TradeManager:
    """
    High-level coordinator for the trading system.
    """

    def __init__(
        self,
        lifecycle_engine: TradeLifecycleEngine,
    ) -> None:
        self._lifecycle_engine = lifecycle_engine

    def start_cycle(self) -> None:
        """
        Synchronize broker state before scanning
        for new opportunities.
        """
        self._lifecycle_engine.synchronize()