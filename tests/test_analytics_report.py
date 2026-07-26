from pathlib import Path
from unittest.mock import MagicMock

import pytest

import analytics.report as report


def test_validate_limit_accepts_positive_value() -> None:
    assert report.validate_limit(100) == 100


def test_validate_limit_rejects_zero() -> None:
    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):
        report.validate_limit(0)


def test_validate_limit_rejects_negative_value() -> None:
    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):
        report.validate_limit(-1)


def test_generate_report_reads_journal(
    monkeypatch,
) -> None:
    journal = MagicMock()

    journal.get_recent_events.return_value = [
        {
            "symbol": "META",
            "status": "candidate_ranked",
            "score": 85.0,
        },
        {
            "symbol": "META",
            "status": "order_submitted",
        },
    ]

    journal_constructor = MagicMock(
        return_value=journal,
    )

    monkeypatch.setattr(
        report,
        "TradeJournal",
        journal_constructor,
    )

    database_path = Path(
        "database/test_journal.db"
    )

    output = report.generate_report(
        database_path=database_path,
        limit=100,
    )

    journal_constructor.assert_called_once_with(
        database_path=str(database_path),
    )

    journal.get_recent_events.assert_called_once_with(
        limit=100,
    )

    assert "TRADE JOURNAL ANALYTICS" in output
    assert "Total Events: 2" in output
    assert "Submitted Orders: 1" in output
    assert "Average Candidate Score: 85.00" in output


def test_build_parser_defaults() -> None:
    parser = report.build_parser()

    arguments = parser.parse_args([])

    assert (
        arguments.database
        == report.DEFAULT_DATABASE_PATH
    )

    assert (
        arguments.limit
        == report.DEFAULT_EVENT_LIMIT
    )


def test_build_parser_accepts_arguments() -> None:
    parser = report.build_parser()

    arguments = parser.parse_args(
        [
            "--database",
            "data/custom.db",
            "--limit",
            "25",
        ]
    )

    assert arguments.database == Path(
        "data/custom.db"
    )

    assert arguments.limit == 25