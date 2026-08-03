from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class SessionSummary:
    candidates_ranked: int
    risk_filtered: int
    preflight_passed: int
    preflight_rejected: int
    execution_disabled: int
    user_cancelled: int
    submitted_verified: int


class SessionStatistics:
    """
    Calculates trading session execution statistics
    from journal events.

    This module contains no database,
    broker, or file-system dependencies.
    """

    @staticmethod
    def calculate(
        events: Iterable[dict[str, Any]],
    ) -> SessionSummary:
        event_list = list(events)

        return SessionSummary(
            candidates_ranked=(
                SessionStatistics._count_status(
                    event_list,
                    "candidate_ranked",
                )
            ),
            risk_filtered=(
                SessionStatistics._count_status(
                    event_list,
                    "risk_filtered",
                )
            ),
            preflight_passed=(
                SessionStatistics._count_status(
                    event_list,
                    "preflight_passed",
                )
            ),
            preflight_rejected=(
                SessionStatistics._count_status(
                    event_list,
                    "preflight_rejected",
                )
            ),
            execution_disabled=(
                SessionStatistics._count_status(
                    event_list,
                    "execution_disabled",
                )
            ),
            user_cancelled=(
                SessionStatistics._count_status(
                    event_list,
                    "user_cancelled",
                )
            ),
            submitted_verified=(
                SessionStatistics._count_status(
                    event_list,
                    "submitted_verified",
                )
            ),
        )

    @staticmethod
    def _count_status(
        events: list[dict[str, Any]],
        status: str,
    ) -> int:
        return sum(
            1
            for event in events
            if event.get("status") == status
        )