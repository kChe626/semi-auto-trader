from pathlib import Path
from unittest.mock import MagicMock

import main


def test_run_production_wires_telegram_trade_approval(
    monkeypatch,
    tmp_path: Path,
) -> None:
    journal = MagicMock()
    repository = MagicMock()
    approval = MagicMock()

    monkeypatch.setattr(
        main,
        "TradeJournal",
        MagicMock(return_value=journal),
    )

    monkeypatch.setattr(
        main,
        "create_trade_repository",
        MagicMock(return_value=repository),
    )

    monkeypatch.setattr(
        main,
        "create_runtime_telegram_approval",
        MagicMock(return_value=approval),
    )

    monkeypatch.setattr(
        main,
        "TELEGRAM_APPROVAL_ENABLED",
        True,
        raising=False,
    )

    run_main = MagicMock()

    monkeypatch.setattr(
        main,
        "main",
        run_main,
    )

    main.run_production(
        database_path=tmp_path / "trades.db",
    )

    run_main.assert_called_once_with(
        notification_sender=main.send_telegram_message,
        journal=journal,
        trade_repository=repository,
        trade_approval=approval,
    )