from __future__ import annotations

import argparse
from pathlib import Path

from analytics.session_statistics import (
    SessionStatistics,
    SessionSummary,
)
from database.trade_journal import (
    DATABASE_PATH,
    TradeJournal,
)


DEFAULT_EVENT_LIMIT = 500


def format_session_report(
    summary: SessionSummary,
) -> str:
    return "\n".join(
        [
            "================================================",
            "TRADING SESSION REPORT",
            "================================================",
            "",
            "Candidates",
            "----------",
            (
                "Candidates Ranked: "
                f"{summary.candidates_ranked}"
            ),
            (
                "Risk Filtered: "
                f"{summary.risk_filtered}"
            ),
            "",
            "Execution",
            "----------",
            (
                "Preflight Passed: "
                f"{summary.preflight_passed}"
            ),
            (
                "Preflight Rejected: "
                f"{summary.preflight_rejected}"
            ),
            (
                "Execution Disabled: "
                f"{summary.execution_disabled}"
            ),
            (
                "User Cancelled: "
                f"{summary.user_cancelled}"
            ),
            (
                "Submitted Verified: "
                f"{summary.submitted_verified}"
            ),
            "",
            "================================================",
        ]
    )


def generate_session_report(
    database_path: Path,
    limit: int,
) -> str:
    journal = TradeJournal(
        database_path=str(database_path)
    )

    events = journal.get_recent_events(
        limit=limit,
    )

    summary = SessionStatistics.calculate(
        events
    )

    return format_session_report(
        summary
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a trading session report "
            "from the SQLite trade journal."
        )
    )

    parser.add_argument(
        "--database",
        type=Path,
        default=DATABASE_PATH,
        help=(
            "Path to the SQLite journal database."
        ),
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_EVENT_LIMIT,
        help=(
            "Maximum number of recent journal "
            "events to analyze."
        ),
    )

    return parser


def validate_limit(
    limit: int,
) -> int:
    if limit <= 0:
        raise ValueError(
            "Event limit must be greater than zero."
        )

    return limit


def main() -> None:
    parser = build_parser()
    arguments = parser.parse_args()

    try:
        report = generate_session_report(
            database_path=arguments.database,
            limit=validate_limit(
                arguments.limit
            ),
        )

    except (OSError, ValueError) as error:
        parser.error(str(error))

    print(report)


if __name__ == "__main__":
    main()