from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Protocol


class TradingClientProtocol(Protocol):
    """
    Minimum Alpaca trading-client operations required
    by the dashboard account service.
    """

    def get_account(self) -> Any:
        ...

    def get_all_positions(self) -> Iterable[Any]:
        ...


@dataclass(frozen=True)
class AccountSummary:
    """
    Read-only Alpaca paper-account information prepared
    for the dashboard.
    """

    status: str
    cash: float
    equity: float
    buying_power: float
    portfolio_value: float
    last_equity: float
    trading_blocked: bool
    account_blocked: bool


@dataclass(frozen=True)
class OpenPosition:
    """
    Normalized open-position information for dashboard
    presentation.
    """

    symbol: str
    side: str
    quantity: float
    average_entry_price: float
    current_price: float
    market_value: float
    cost_basis: float
    unrealized_profit_loss: float
    unrealized_profit_loss_percent: float


@dataclass(frozen=True)
class AccountDashboardData:
    """
    Complete read-only Alpaca account snapshot.
    """

    account: AccountSummary
    open_positions: tuple[OpenPosition, ...]


class AccountService:
    """
    Loads and normalizes Alpaca paper-account data for
    the future Streamlit dashboard.

    This service performs read-only broker operations.
    It does not submit, replace, or cancel orders.
    """

    def __init__(
        self,
        trading_client: TradingClientProtocol,
    ) -> None:
        self._trading_client = trading_client

    def load_account_data(
        self,
    ) -> AccountDashboardData:
        account = self._trading_client.get_account()

        positions = tuple(
            self._build_position(position)
            for position
            in self._trading_client.get_all_positions()
        )

        return AccountDashboardData(
            account=self._build_account_summary(
                account
            ),
            open_positions=positions,
        )

    @classmethod
    def _build_account_summary(
        cls,
        account: Any,
    ) -> AccountSummary:
        return AccountSummary(
            status=cls._normalize_text(
                getattr(account, "status", "")
            ),
            cash=cls._to_float(
                getattr(account, "cash", 0.0)
            ),
            equity=cls._to_float(
                getattr(account, "equity", 0.0)
            ),
            buying_power=cls._to_float(
                getattr(
                    account,
                    "buying_power",
                    0.0,
                )
            ),
            portfolio_value=cls._to_float(
                getattr(
                    account,
                    "portfolio_value",
                    0.0,
                )
            ),
            last_equity=cls._to_float(
                getattr(
                    account,
                    "last_equity",
                    0.0,
                )
            ),
            trading_blocked=bool(
                getattr(
                    account,
                    "trading_blocked",
                    False,
                )
            ),
            account_blocked=bool(
                getattr(
                    account,
                    "account_blocked",
                    False,
                )
            ),
        )

    @classmethod
    def _build_position(
        cls,
        position: Any,
    ) -> OpenPosition:
        return OpenPosition(
            symbol=cls._normalize_text(
                getattr(position, "symbol", "")
            ).upper(),
            side=cls._normalize_text(
                getattr(position, "side", "")
            ).lower(),
            quantity=cls._to_float(
                getattr(position, "qty", 0.0)
            ),
            average_entry_price=cls._to_float(
                getattr(
                    position,
                    "avg_entry_price",
                    0.0,
                )
            ),
            current_price=cls._to_float(
                getattr(
                    position,
                    "current_price",
                    0.0,
                )
            ),
            market_value=cls._to_float(
                getattr(
                    position,
                    "market_value",
                    0.0,
                )
            ),
            cost_basis=cls._to_float(
                getattr(
                    position,
                    "cost_basis",
                    0.0,
                )
            ),
            unrealized_profit_loss=cls._to_float(
                getattr(
                    position,
                    "unrealized_pl",
                    0.0,
                )
            ),
            unrealized_profit_loss_percent=(
                cls._to_float(
                    getattr(
                        position,
                        "unrealized_plpc",
                        0.0,
                    )
                )
            ),
        )

    @staticmethod
    def _normalize_text(
        value: Any,
    ) -> str:
        if value is None:
            return ""

        raw_value = getattr(
            value,
            "value",
            value,
        )

        return str(raw_value).strip()

    @staticmethod
    def _to_float(
        value: Any,
    ) -> float:
        if value is None:
            return 0.0

        try:
            return float(value)
        except (
            TypeError,
            ValueError,
        ) as error:
            raise ValueError(
                "Broker numeric value must be "
                f"convertible to float: {value!r}"
            ) from error