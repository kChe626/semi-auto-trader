from __future__ import annotations

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
    entry_price: float | None = None,
    stop_price: float | None = None,
    target_price: float | None = None,
    quantity: float | None = None,
    total_risk: float | None = None,
    risk_reward_ratio: float | None = None,
    reason: str | None = None,
    trade_id: Any | None = None,
    order_id: Any | None = None,
) -> int | None:
    """
    Record a journal event without allowing a database failure
    to stop the trading cycle.
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
            entry_price=entry_price,
            stop_price=stop_price,
            target_price=target_price,
            quantity=quantity,
            total_risk=total_risk,
            risk_reward_ratio=risk_reward_ratio,
            reason=reason,
            trade_id=trade_id,
            order_id=order_id,
        )
    except Exception as error:
        print(
            "Warning: unable to record journal event "
            f"for {symbol}: {error}"
        )
        return None


def record_plan_safely(
    journal: TradeJournal | None,
    *,
    plan: Any,
    status: str,
    score: float | None = None,
    reason: str | None = None,
    trade_id: Any | None = None,
    order_id: Any | None = None,
    asset_type: str = "stock",
) -> int | None:
    """
    Record a trade plan without allowing a database failure
    to stop the trading cycle.
    """
    if journal is None:
        return None

    try:
        return journal.record_plan(
            plan=plan,
            status=status,
            score=score,
            reason=reason,
            trade_id=trade_id,
            order_id=order_id,
            asset_type=asset_type,
        )
    except Exception as error:
        symbol = getattr(
            plan,
            "symbol",
            "unknown",
        )

        print(
            "Warning: unable to record trade plan "
            f"for {symbol}: {error}"
        )
        return None