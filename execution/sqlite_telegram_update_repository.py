from __future__ import annotations

import sqlite3
from pathlib import Path


class SqliteTelegramUpdateRepository:
    def __init__(
        self,
        *,
        database_path: Path,
    ) -> None:
        self._database_path = database_path
        self._initialize()

    def _initialize(self) -> None:
        with sqlite3.connect(
            self._database_path
        ) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS telegram_updates (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    last_update_id INTEGER NOT NULL
                )
                """
            )

    def get_last_update_id(
        self,
    ) -> int | None:
        with sqlite3.connect(
            self._database_path
        ) as connection:
            row = connection.execute(
                """
                SELECT last_update_id
                FROM telegram_updates
                WHERE id = 1
                """
            ).fetchone()

        if row is None:
            return None

        return int(row[0])

    def save_last_update_id(
        self,
        update_id: int,
    ) -> None:
        with sqlite3.connect(
            self._database_path
        ) as connection:
            connection.execute(
                """
                INSERT INTO telegram_updates (
                    id,
                    last_update_id
                )
                VALUES (
                    1,
                    ?
                )
                ON CONFLICT(id)
                DO UPDATE SET
                    last_update_id = excluded.last_update_id
                """,
                (
                    update_id,
                ),
            )