from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AccountMetricsViewModel:
    """
    Display-ready account metrics for the dashboard.
    """

    status: str
    cash: str
    equity: str
    buying_power: str
    portfolio_value: str
    daily_change: str
    daily_change_percent: str
    trading_status: str


@dataclass(frozen=True)
class PositionRowViewModel:
    """
    Display-ready open-position row.
    """

    symbol: str
    side: str
    quantity: str
    average_entry_price: str
    current_price: str
    market_value: str
    cost_basis: str
    unrealized_profit_loss: str
    unrealized_profit_loss_percent: str


@dataclass(frozen=True)
class AccountSectionViewModel:
    """
    Complete presentation model for the account section.
    """

    metrics: AccountMetricsViewModel
    positions: tuple[PositionRowViewModel, ...]
    has_open_positions: bool