from typing import Any

from database.trade_journal import TradeJournal


def record_event_safely(
    journal: TradeJournal | None,
    *,
    symbol: str,
    status: str,
    asset_type: str = "stock",
    signal_type: str | None = None,
    score: float | None = None,
    reason: str | None = None,
    order_id: Any | None = None,
) -> int | None:
    """
    Record a journal event without allowing a database failure
    to stop the trading workflow.
    """
    if journal is None:
        return None

    try:
        return journal.record_event(
            symbol=symbol,
            status=status,
            asset_type=asset_type,
            signal_type=signal_type,
            score=score,
            reason=reason,
            order_id=order_id,
        )
    except Exception as error:
        print(
            "\nTrade journal write failed: "
            f"{error}"
        )
        return None


def record_plan_safely(
    journal: TradeJournal | None,
    *,
    plan: Any,
    status: str,
    score: float | None = None,
    reason: str | None = None,
    order_id: Any | None = None,
    asset_type: str = "stock",
) -> int | None:
    """
    Record a trade plan without allowing a database failure
    to stop the trading workflow.
    """
    if journal is None:
        return None

    try:
        return journal.record_plan(
            plan=plan,
            status=status,
            score=score,
            reason=reason,
            order_id=order_id,
            asset_type=asset_type,
        )
    except Exception as error:
        print(
            "\nTrade journal write failed: "
            f"{error}"
        )
        return None