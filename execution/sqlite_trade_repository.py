from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from models.trade import Trade, TradeStatus


class SqliteTradeRepository:
    def __init__(
        self,
        database_path: str | Path,
    ) -> None:
        self._database_path = Path(database_path)
        self._create_table()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(
            self._database_path
        )

    def _create_table(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS trades (
                    trade_id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    status TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    stop_price REAL NOT NULL,
                    target_price REAL NOT NULL,
                    parent_order_id TEXT
                )
                """
            )

    def save(
        self,
        trade: Trade,
    ) -> None:
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO trades (
                        trade_id,
                        symbol,
                        quantity,
                        status,
                        entry_price,
                        stop_price,
                        target_price,
                        parent_order_id
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    self._trade_to_values(trade),
                )
        except sqlite3.IntegrityError as exc:
            raise ValueError(
                f"trade already exists: {trade.trade_id}"
            ) from exc

    def get(
        self,
        trade_id: str,
    ) -> Trade | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    trade_id,
                    symbol,
                    quantity,
                    status,
                    entry_price,
                    stop_price,
                    target_price,
                    parent_order_id
                FROM trades
                WHERE trade_id = ?
                """,
                (trade_id,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_trade(row)

    def get_all(
        self,
    ) -> list[Trade]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    trade_id,
                    symbol,
                    quantity,
                    status,
                    entry_price,
                    stop_price,
                    target_price,
                    parent_order_id
                FROM trades
                ORDER BY rowid
                """
            ).fetchall()

        return [
            self._row_to_trade(row)
            for row in rows
        ]

    def update(
        self,
        trade: Trade,
    ) -> None:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE trades
                SET
                    symbol = ?,
                    quantity = ?,
                    status = ?,
                    entry_price = ?,
                    stop_price = ?,
                    target_price = ?,
                    parent_order_id = ?
                WHERE trade_id = ?
                """,
                (
                    trade.symbol,
                    trade.quantity,
                    trade.status.value,
                    trade.entry_price,
                    trade.stop_price,
                    trade.target_price,
                    trade.parent_order_id,
                    trade.trade_id,
                ),
            )

        if cursor.rowcount == 0:
            raise ValueError(
                f"trade does not exist: {trade.trade_id}"
            )

    def remove(
        self,
        trade_id: str,
    ) -> None:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM trades
                WHERE trade_id = ?
                """,
                (trade_id,),
            )

        if cursor.rowcount == 0:
            raise ValueError(
                f"trade does not exist: {trade_id}"
            )

    def get_open(
        self,
    ) -> list[Trade]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    trade_id,
                    symbol,
                    quantity,
                    status,
                    entry_price,
                    stop_price,
                    target_price,
                    parent_order_id
                FROM trades
                WHERE status IN (?, ?, ?)
                ORDER BY rowid
                """,
                (
                    TradeStatus.SUBMITTED.value,
                    TradeStatus.PARTIALLY_FILLED.value,
                    TradeStatus.FILLED.value,
                ),
            ).fetchall()

        return [
            self._row_to_trade(row)
            for row in rows
        ]

    @staticmethod
    def _trade_to_values(
        trade: Trade,
    ) -> tuple[Any, ...]:
        return (
            trade.trade_id,
            trade.symbol,
            trade.quantity,
            trade.status.value,
            trade.entry_price,
            trade.stop_price,
            trade.target_price,
            trade.parent_order_id,
        )

    @staticmethod
    def _row_to_trade(
        row: sqlite3.Row | tuple[Any, ...],
    ) -> Trade:
        return Trade(
            trade_id=row[0],
            symbol=row[1],
            quantity=row[2],
            status=TradeStatus(row[3]),
            entry_price=row[4],
            stop_price=row[5],
            target_price=row[6],
            parent_order_id=row[7],
        )