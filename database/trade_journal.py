from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DATABASE_PATH = Path("database") / "trade_journal.db"


class TradeJournal:
    def __init__(
        self,
        database_path: Path | str = DATABASE_PATH,
    ) -> None:
        self.database_path = Path(database_path)

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._create_tables()
        self._migrate_schema()
        self._create_indexes()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.database_path
        )

        connection.row_factory = sqlite3.Row

        return connection

    def _create_tables(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS trade_journal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    asset_type TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    signal_type TEXT,
                    score REAL,
                    entry_price REAL,
                    stop_price REAL,
                    target_price REAL,
                    quantity REAL,
                    total_risk REAL,
                    risk_reward_ratio REAL,
                    status TEXT NOT NULL,
                    reason TEXT,
                    trade_id TEXT,
                    order_id TEXT,
                    exit_price REAL,
                    exited_at TEXT,
                    realized_pl REAL,
                    r_multiple REAL,
                    holding_duration_seconds REAL
                )
                """
            )

    def _migrate_schema(self) -> None:
        """
        Add columns introduced after the original
        database schema was created.
        """
        columns = {
            "trade_id": "TEXT",
            "exit_price": "REAL",
            "exited_at": "TEXT",
            "realized_pl": "REAL",
            "r_multiple": "REAL",
            "holding_duration_seconds": "REAL",
        }

        for column_name, column_type in columns.items():
            self._ensure_column(
                column_name=column_name,
                column_type=column_type,
            )

    def _ensure_column(
        self,
        *,
        column_name: str,
        column_type: str,
    ) -> None:
        with self._connect() as connection:
            existing_columns = connection.execute(
                """
                PRAGMA table_info(trade_journal)
                """
            ).fetchall()

            existing_column_names = {
                row["name"]
                for row in existing_columns
            }

            if column_name in existing_column_names:
                return

            connection.execute(
                f"""
                ALTER TABLE trade_journal
                ADD COLUMN {column_name} {column_type}
                """
            )

    def _create_indexes(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_trade_journal_order_id
                ON trade_journal(order_id)
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_trade_journal_trade_id
                ON trade_journal(trade_id)
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_trade_journal_symbol
                ON trade_journal(symbol)
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_trade_journal_status
                ON trade_journal(status)
                """
            )

    @staticmethod
    def _normalize_identifier(
        value: Any | None,
    ) -> str | None:
        if value is None:
            return None

        normalized_value = str(value).strip()

        if not normalized_value:
            return None

        return normalized_value

    @staticmethod
    def _require_identifier(
        value: Any,
        field_name: str,
    ) -> str:
        normalized_value = (
            TradeJournal._normalize_identifier(
                value
            )
        )

        if normalized_value is None:
            raise ValueError(
                f"{field_name} cannot be empty"
            )

        return normalized_value

    @staticmethod
    def _normalize_symbol(
        symbol: str,
    ) -> str:
        normalized_symbol = (
            str(symbol).strip().upper()
        )

        if not normalized_symbol:
            raise ValueError(
                "symbol cannot be empty"
            )

        return normalized_symbol

    def record_event(
        self,
        *,
        symbol: str,
        status: str,
        asset_type: str = "stock",
        signal_type: str | None = None,
        score: float | None = None,
        entry_price: float | None = None,
        stop_price: float | None = None,
        target_price: float | None = None,
        quantity: float | None = None,
        total_risk: float | None = None,
        risk_reward_ratio: float | None = None,
        reason: str | None = None,
        trade_id: Any | None = None,
        order_id: Any | None = None,
        exit_price: float | None = None,
        exited_at: str | None = None,
        realized_pl: float | None = None,
        r_multiple: float | None = None,
        holding_duration_seconds: float | None = None,
    ) -> int:
        normalized_symbol = self._normalize_symbol(
            symbol
        )

        normalized_status = str(
            status
        ).strip()

        if not normalized_status:
            raise ValueError(
                "status cannot be empty"
            )

        normalized_asset_type = str(
            asset_type
        ).strip()

        if not normalized_asset_type:
            raise ValueError(
                "asset_type cannot be empty"
            )

        normalized_trade_id = (
            self._normalize_identifier(
                trade_id
            )
        )

        normalized_order_id = (
            self._normalize_identifier(
                order_id
            )
        )

        normalized_exited_at = (
            self._normalize_identifier(
                exited_at
            )
        )

        created_at = datetime.now(
            timezone.utc
        ).isoformat()

        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO trade_journal (
                    created_at,
                    asset_type,
                    symbol,
                    signal_type,
                    score,
                    entry_price,
                    stop_price,
                    target_price,
                    quantity,
                    total_risk,
                    risk_reward_ratio,
                    status,
                    reason,
                    trade_id,
                    order_id,
                    exit_price,
                    exited_at,
                    realized_pl,
                    r_multiple,
                    holding_duration_seconds
                )
                VALUES (
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?
                )
                """,
                (
                    created_at,
                    normalized_asset_type,
                    normalized_symbol,
                    signal_type,
                    score,
                    entry_price,
                    stop_price,
                    target_price,
                    quantity,
                    total_risk,
                    risk_reward_ratio,
                    normalized_status,
                    reason,
                    normalized_trade_id,
                    normalized_order_id,
                    exit_price,
                    normalized_exited_at,
                    realized_pl,
                    r_multiple,
                    holding_duration_seconds,
                ),
            )

            return int(cursor.lastrowid)

    def record_plan(
        self,
        *,
        plan: Any,
        status: str,
        score: float | None = None,
        reason: str | None = None,
        trade_id: Any | None = None,
        order_id: Any | None = None,
        asset_type: str = "stock",
    ) -> int:
        return self.record_event(
            symbol=plan.symbol,
            status=status,
            asset_type=asset_type,
            signal_type=getattr(
                plan,
                "signal_type",
                None,
            ),
            score=score,
            entry_price=getattr(
                plan,
                "entry_price",
                None,
            ),
            stop_price=getattr(
                plan,
                "stop_price",
                None,
            ),
            target_price=getattr(
                plan,
                "target_price",
                None,
            ),
            quantity=getattr(
                plan,
                "quantity",
                None,
            ),
            total_risk=getattr(
                plan,
                "total_risk",
                None,
            ),
            risk_reward_ratio=getattr(
                plan,
                "risk_reward_ratio",
                None,
            ),
            reason=reason,
            trade_id=trade_id,
            order_id=order_id,
        )

    def get_recent_events(
        self,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        if limit <= 0:
            raise ValueError(
                "limit must be greater than zero"
            )

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM trade_journal
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    def get_events_by_order_id(
        self,
        order_id: Any,
    ) -> list[dict[str, Any]]:
        normalized_order_id = (
            self._require_identifier(
                order_id,
                "order_id",
            )
        )

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM trade_journal
                WHERE order_id = ?
                ORDER BY id ASC
                """,
                (normalized_order_id,),
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    def get_latest_event_by_order_id(
        self,
        order_id: Any,
    ) -> dict[str, Any] | None:
        normalized_order_id = (
            self._require_identifier(
                order_id,
                "order_id",
            )
        )

        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM trade_journal
                WHERE order_id = ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (normalized_order_id,),
            ).fetchone()

        if row is None:
            return None

        return dict(row)

    def get_tracked_order_ids(
        self,
    ) -> set[str]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT DISTINCT order_id
                FROM trade_journal
                WHERE order_id IS NOT NULL
                  AND TRIM(order_id) <> ''
                """
            ).fetchall()

        return {
            str(row["order_id"])
            for row in rows
        }

    def get_events_by_trade_id(
        self,
        trade_id: Any,
    ) -> list[dict[str, Any]]:
        normalized_trade_id = (
            self._require_identifier(
                trade_id,
                "trade_id",
            )
        )

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM trade_journal
                WHERE trade_id = ?
                ORDER BY id ASC
                """,
                (normalized_trade_id,),
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    def get_latest_event_by_trade_id(
        self,
        trade_id: Any,
    ) -> dict[str, Any] | None:
        normalized_trade_id = (
            self._require_identifier(
                trade_id,
                "trade_id",
            )
        )

        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM trade_journal
                WHERE trade_id = ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (normalized_trade_id,),
            ).fetchone()

        if row is None:
            return None

        return dict(row)

    def get_tracked_trade_ids(
        self,
    ) -> set[str]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT DISTINCT trade_id
                FROM trade_journal
                WHERE trade_id IS NOT NULL
                  AND TRIM(trade_id) <> ''
                """
            ).fetchall()

        return {
            str(row["trade_id"])
            for row in rows
        }

    def get_events_by_symbol(
        self,
        symbol: str,
    ) -> list[dict[str, Any]]:
        normalized_symbol = (
            self._normalize_symbol(
                symbol
            )
        )

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM trade_journal
                WHERE UPPER(symbol) = ?
                ORDER BY id ASC
                """,
                (normalized_symbol,),
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    def get_latest_event_by_symbol(
        self,
        symbol: str,
    ) -> dict[str, Any] | None:
        normalized_symbol = (
            self._normalize_symbol(
                symbol
            )
        )

        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM trade_journal
                WHERE UPPER(symbol) = ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (normalized_symbol,),
            ).fetchone()

        if row is None:
            return None

        return dict(row)

    def get_open_trade_events(
        self,
    ) -> list[dict[str, Any]]:
        """
        Return each trade's latest event when that event
        is position_open.

        Trades whose latest event is position_closed are
        not returned.
        """
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT journal.*
                FROM trade_journal AS journal

                INNER JOIN (
                    SELECT
                        trade_id,
                        MAX(id) AS latest_id
                    FROM trade_journal
                    WHERE trade_id IS NOT NULL
                      AND TRIM(trade_id) <> ''
                    GROUP BY trade_id
                ) AS latest
                    ON journal.id = latest.latest_id

                WHERE journal.status = 'position_open'

                ORDER BY journal.id ASC
                """
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    def get_closed_trade_events(
        self,
    ) -> list[dict[str, Any]]:
        """
        Return completed trades in the format required
        by ClosedTradeRepository.

        Each result combines the latest position_closed
        event with the preceding position_open event for
        the same trade_id.
        """
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    closed_event.trade_id
                        AS trade_id,

                    closed_event.symbol
                        AS symbol,

                    COALESCE(
                        closed_event.entry_price,
                        open_event.entry_price
                    ) AS entry_price,

                    closed_event.exit_price
                        AS exit_price,

                    COALESCE(
                        closed_event.quantity,
                        open_event.quantity
                    ) AS quantity,

                    closed_event.realized_pl
                        AS realized_pl,

                    closed_event.r_multiple
                        AS r_multiple,

                    COALESCE(
                        closed_event.holding_duration_seconds,
                        (
                            julianday(
                                COALESCE(
                                    closed_event.exited_at,
                                    closed_event.created_at
                                )
                            )
                            -
                            julianday(
                                open_event.created_at
                            )
                        ) * 86400.0
                    ) AS holding_duration_seconds,

                    open_event.created_at
                        AS opened_at,

                    COALESCE(
                        closed_event.exited_at,
                        closed_event.created_at
                    ) AS closed_at

                FROM trade_journal AS closed_event

                INNER JOIN trade_journal AS open_event
                    ON open_event.id = (
                        SELECT MAX(candidate.id)
                        FROM trade_journal AS candidate
                        WHERE candidate.trade_id
                              = closed_event.trade_id
                          AND candidate.status
                              = 'position_open'
                          AND candidate.id
                              < closed_event.id
                    )

                WHERE closed_event.status
                      = 'position_closed'

                  AND closed_event.trade_id
                      IS NOT NULL

                  AND TRIM(
                      closed_event.trade_id
                  ) <> ''

                  AND closed_event.exit_price
                      IS NOT NULL

                  AND closed_event.realized_pl
                      IS NOT NULL

                  AND closed_event.r_multiple
                      IS NOT NULL

                  AND closed_event.id = (
                      SELECT MAX(latest_closed.id)
                      FROM trade_journal
                           AS latest_closed
                      WHERE latest_closed.trade_id
                            = closed_event.trade_id
                        AND latest_closed.status
                            = 'position_closed'
                  )

                ORDER BY closed_event.id ASC
                """
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]