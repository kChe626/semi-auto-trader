from pathlib import Path

from analytics.session_report import (
    generate_session_report,
)


def test_generate_session_report_reads_journal(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "journal.db"

    report = generate_session_report(
        database_path=database_path,
        limit=100,
    )

    assert "TRADING SESSION REPORT" in report