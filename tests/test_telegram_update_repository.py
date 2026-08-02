from pathlib import Path

from execution.sqlite_telegram_update_repository import (
    SqliteTelegramUpdateRepository,
)


def test_save_and_get_last_update_id(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "trades.db"

    repository = (
        SqliteTelegramUpdateRepository(
            database_path=database_path,
        )
    )

    assert (
        repository.get_last_update_id()
        is None
    )

    repository.save_last_update_id(
        123
    )

    assert (
        repository.get_last_update_id()
        == 123
    )


def test_updates_replace_previous_value(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "trades.db"

    repository = (
        SqliteTelegramUpdateRepository(
            database_path=database_path,
        )
    )

    repository.save_last_update_id(
        100
    )

    repository.save_last_update_id(
        200
    )

    assert (
        repository.get_last_update_id()
        == 200
    )