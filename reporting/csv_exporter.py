from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from models.closed_trade import ClosedTrade


class ClosedTradeCsvExporter:
    """
    Exports completed trades to a CSV file.

    The generated file can be opened directly in Excel,
    Google Sheets, or other spreadsheet applications.
    """

    FIELDNAMES = (
        "trade_id",
        "symbol",
        "entry_price",
        "exit_price",
        "quantity",
        "realized_pl",
        "r_multiple",
        "holding_duration_seconds",
        "opened_at",
        "closed_at",
    )

    @classmethod
    def export(
        cls,
        trades: Iterable[ClosedTrade],
        output_path: str | Path,
    ) -> Path:
        normalized_trades = list(trades)

        cls._validate_trades(
            normalized_trades
        )

        path = Path(output_path)

        if path.suffix.lower() != ".csv":
            raise ValueError(
                "output_path must end with .csv"
            )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with path.open(
            mode="w",
            newline="",
            encoding="utf-8-sig",
        ) as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=cls.FIELDNAMES,
            )

            writer.writeheader()

            for trade in normalized_trades:
                writer.writerow(
                    cls._trade_to_row(trade)
                )

        return path

    @staticmethod
    def _trade_to_row(
        trade: ClosedTrade,
    ) -> dict[str, object]:
        return {
            "trade_id": trade.trade_id,
            "symbol": trade.symbol,
            "entry_price": trade.entry_price,
            "exit_price": trade.exit_price,
            "quantity": trade.quantity,
            "realized_pl": trade.realized_pl,
            "r_multiple": trade.r_multiple,
            "holding_duration_seconds": (
                trade.holding_duration_seconds
            ),
            "opened_at": (
                trade.opened_at.isoformat()
            ),
            "closed_at": (
                trade.closed_at.isoformat()
            ),
        }

    @staticmethod
    def _validate_trades(
        trades: list[ClosedTrade],
    ) -> None:
        for trade in trades:
            if not isinstance(
                trade,
                ClosedTrade,
            ):
                raise TypeError(
                    "all trades must be "
                    "ClosedTrade instances"
                )