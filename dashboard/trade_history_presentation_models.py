from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TradeHistoryRowViewModel:
    trade_id: str
    symbol: str
    side: str
    opened_at: str
    closed_at: str
    quantity: str
    entry_price: str
    exit_price: str
    realized_profit_loss: str
    r_multiple: str
    holding_duration: str


@dataclass(frozen=True, slots=True)
class TradeHistorySectionViewModel:
    rows: tuple[TradeHistoryRowViewModel, ...]

    @property
    def has_rows(self) -> bool:
        return bool(self.rows)