from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class TradeAnalyticsSummary:
    total_events: int
    unique_symbols: int
    submitted_orders: int
    cancelled_trades: int
    direction_filtered: int
    preflight_rejections: int
    average_candidate_score: float | None
    status_counts: dict[str, int]
    direction_filter_reason_counts: dict[str, int]
    rejection_reason_counts: dict[str, int]


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip()


def _get_status(event: dict[str, Any]) -> str:
    return _normalize_text(
        event.get("status")
    ).lower()


def _get_symbol(event: dict[str, Any]) -> str:
    return _normalize_text(
        event.get("symbol")
    ).upper()


def _get_score(
    event: dict[str, Any],
) -> float | None:
    value = event.get("score")

    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _split_reasons(reason: Any) -> list[str]:
    text = _normalize_text(reason)

    if not text:
        return []

    reasons = []

    for item in text.split(";"):
        cleaned = item.strip().rstrip(".")

        if cleaned:
            reasons.append(cleaned)

    return reasons


def _sorted_counts(
    counter: Counter[str],
) -> dict[str, int]:
    return dict(
        sorted(
            counter.items(),
            key=lambda item: (
                -item[1],
                item[0],
            ),
        )
    )


def summarize_trade_events(
    events: Iterable[dict[str, Any]],
) -> TradeAnalyticsSummary:
    event_list = list(events)

    status_counter: Counter[str] = Counter()
    direction_filter_counter: Counter[str] = (
        Counter()
    )
    rejection_counter: Counter[str] = Counter()

    symbols: set[str] = set()
    candidate_scores: list[float] = []

    for event in event_list:
        status = _get_status(event)
        symbol = _get_symbol(event)

        if status:
            status_counter[status] += 1

        if symbol:
            symbols.add(symbol)

        if status == "candidate_ranked":
            score = _get_score(event)

            if score is not None:
                candidate_scores.append(score)

        if status == "direction_filtered":
            for reason in _split_reasons(
                event.get("reason")
            ):
                direction_filter_counter[
                    reason
                ] += 1

        if status == "preflight_rejected":
            for reason in _split_reasons(
                event.get("reason")
            ):
                rejection_counter[reason] += 1

    average_score: float | None = None

    if candidate_scores:
        average_score = round(
            sum(candidate_scores)
            / len(candidate_scores),
            2,
        )

    submitted_orders = sum(
        count
        for status, count
        in status_counter.items()
        if status
        in {
            "order_submitted",
            "submitted",
            "paper_order_submitted",
            "submitted_verified",
        }
    )

    cancelled_trades = sum(
        count
        for status, count
        in status_counter.items()
        if status
        in {
            "cancelled",
            "confirmation_cancelled",
            "user_cancelled",
        }
    )

    return TradeAnalyticsSummary(
        total_events=len(event_list),
        unique_symbols=len(symbols),
        submitted_orders=submitted_orders,
        cancelled_trades=cancelled_trades,
        direction_filtered=status_counter.get(
            "direction_filtered",
            0,
        ),
        preflight_rejections=status_counter.get(
            "preflight_rejected",
            0,
        ),
        average_candidate_score=average_score,
        status_counts=dict(
            sorted(status_counter.items())
        ),
        direction_filter_reason_counts=(
            _sorted_counts(
                direction_filter_counter
            )
        ),
        rejection_reason_counts=_sorted_counts(
            rejection_counter
        ),
    )


def format_trade_analytics(
    summary: TradeAnalyticsSummary,
) -> str:
    lines = [
        "=" * 60,
        "TRADE JOURNAL ANALYTICS",
        "=" * 60,
        f"Total Events: {summary.total_events}",
        (
            "Unique Symbols: "
            f"{summary.unique_symbols}"
        ),
        (
            "Submitted Orders: "
            f"{summary.submitted_orders}"
        ),
        (
            "Cancelled Trades: "
            f"{summary.cancelled_trades}"
        ),
        (
            "Direction Filtered: "
            f"{summary.direction_filtered}"
        ),
        (
            "Preflight Rejections: "
            f"{summary.preflight_rejections}"
        ),
    ]

    if summary.average_candidate_score is None:
        lines.append(
            "Average Candidate Score: N/A"
        )
    else:
        lines.append(
            "Average Candidate Score: "
            f"{summary.average_candidate_score:.2f}"
        )

    lines.extend(
        [
            "",
            "STATUS COUNTS",
            "-" * 60,
        ]
    )

    if summary.status_counts:
        for status, count in (
            summary.status_counts.items()
        ):
            lines.append(
                f"{status}: {count}"
            )
    else:
        lines.append(
            "No journal statuses found."
        )

    lines.extend(
        [
            "",
            "DIRECTION FILTER REASONS",
            "-" * 60,
        ]
    )

    if summary.direction_filter_reason_counts:
        for reason, count in (
            summary
            .direction_filter_reason_counts
            .items()
        ):
            lines.append(
                f"{reason}: {count}"
            )
    else:
        lines.append(
            "No direction filter reasons found."
        )

    lines.extend(
        [
            "",
            "PREFLIGHT REJECTION REASONS",
            "-" * 60,
        ]
    )

    if summary.rejection_reason_counts:
        for reason, count in (
            summary.rejection_reason_counts.items()
        ):
            lines.append(
                f"{reason}: {count}"
            )
    else:
        lines.append(
            "No preflight rejection reasons found."
        )

    lines.append("=" * 60)

    return "\n".join(lines)