from __future__ import annotations

import argparse
from pathlib import Path

from analytics.trade_analytics import (
    format_trade_analytics,
    summarize_trade_events,
)
from database.trade_journal import TradeJournal


DEFAULT_DATABASE_PATH = Path("database/trade_journal.db")
DEFAULT_EVENT_LIMIT = 500


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate an analytics report from the "
            "SQLite trade journal."
        )
    )

    parser.add_argument(
        "--database",
        type=Path,
        default=DEFAULT_DATABASE_PATH,
        help=(
            "Path to the SQLite journal database. "
            f"Default: {DEFAULT_DATABASE_PATH}"
        ),
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_EVENT_LIMIT,
        help=(
            "Maximum number of recent journal events "
            f"to analyze. Default: {DEFAULT_EVENT_LIMIT}"
        ),
    )

    return parser


def validate_limit(limit: int) -> int:
    if limit <= 0:
        raise ValueError(
            "Event limit must be greater than zero."
        )

    return limit


def generate_report(
    database_path: Path,
    limit: int,
) -> str:
    validated_limit = validate_limit(limit)

    journal = TradeJournal(
        database_path=str(database_path)
    )

    events = journal.get_recent_events(
    limit=validated_limit
    )

    summary = summarize_trade_events(events)

    return format_trade_analytics(summary)


def main() -> None:
    parser = build_parser()
    arguments = parser.parse_args()

    try:
        report = generate_report(
            database_path=arguments.database,
            limit=arguments.limit,
        )
    except (OSError, ValueError) as error:
        parser.error(str(error))

    print(report)


if __name__ == "__main__":
    main()