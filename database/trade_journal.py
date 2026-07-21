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
                    order_id TEXT
                )
                """
            )

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
        order_id: Any | None = None,
    ) -> int:
        created_at = datetime.now(
            timezone.utc
        ).isoformat()

        normalized_order_id = (
            str(order_id)
            if order_id is not None
            else None
        )

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
                    order_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
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
                    normalized_order_id,
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