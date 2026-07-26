from __future__ import annotations

from pathlib import Path
from typing import Callable, Iterable

from models.closed_trade import ClosedTrade
from reporting.csv_exporter import (
    ClosedTradeCsvExporter,
)


ClosedTradeLoader = Callable[
    [],
    Iterable[ClosedTrade],
]


class ClosedTradeReportService:
    """
    Loads completed trades and exports them to CSV.

    The service is intentionally independent of the
    underlying database or repository implementation.
    """

    def __init__(
        self,
        load_closed_trades: ClosedTradeLoader,
    ) -> None:
        if not callable(load_closed_trades):
            raise TypeError(
                "load_closed_trades must be callable"
            )

        self._load_closed_trades = (
            load_closed_trades
        )

    def export_csv(
        self,
        output_path: str | Path,
    ) -> Path:
        trades = list(
            self._load_closed_trades()
        )

        return ClosedTradeCsvExporter.export(
            trades,
            output_path,
        )