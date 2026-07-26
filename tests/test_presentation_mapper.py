from __future__ import annotations

from dashboard.account_service import (
    AccountDashboardData,
    AccountSummary,
    OpenPosition,
)
from dashboard.presentation_mapper import (
    AccountPresentationMapper,
)
from dashboard.presentation_models import (
    AccountMetricsViewModel,
    AccountSectionViewModel,
    PositionRowViewModel,
)


def make_account_data(
    *,
    equity: float = 101500.0,
    last_equity: float = 100000.0,
    trading_blocked: bool = False,
    account_blocked: bool = False,
    positions: tuple[OpenPosition, ...] = (),
) -> AccountDashboardData:
    return AccountDashboardData(
        account=AccountSummary(
            status="ACTIVE",
            cash=95000.5,
            equity=equity,
            buying_power=380000.0,
            portfolio_value=101500.0,
            last_equity=last_equity,
            trading_blocked=trading_blocked,
            account_blocked=account_blocked,
        ),
        open_positions=positions,
    )


def make_position() -> OpenPosition:
    return OpenPosition(
        symbol="AAPL",
        side="long",
        quantity=10.0,
        average_entry_price=200.0,
        current_price=205.0,
        market_value=2050.0,
        cost_basis=2000.0,
        unrealized_profit_loss=50.0,
        unrealized_profit_loss_percent=0.025,
    )


def test_map_account_section_returns_view_model() -> None:
    mapper = AccountPresentationMapper()

    result = mapper.map_account_section(
        make_account_data()
    )

    assert isinstance(
        result,
        AccountSectionViewModel,
    )
    assert isinstance(
        result.metrics,
        AccountMetricsViewModel,
    )


def test_account_metrics_are_formatted() -> None:
    mapper = AccountPresentationMapper()

    result = mapper.map_account_section(
        make_account_data()
    )

    assert result.metrics == AccountMetricsViewModel(
        status="ACTIVE",
        cash="$95,000.50",
        equity="$101,500.00",
        buying_power="$380,000.00",
        portfolio_value="$101,500.00",
        daily_change="+$1,500.00",
        daily_change_percent="+1.50%",
        trading_status="Trading Enabled",
    )


def test_negative_daily_change_is_formatted() -> None:
    mapper = AccountPresentationMapper()

    result = mapper.map_account_section(
        make_account_data(
            equity=99000.0,
            last_equity=100000.0,
        )
    )

    assert result.metrics.daily_change == (
        "-$1,000.00"
    )
    assert result.metrics.daily_change_percent == (
        "-1.00%"
    )


def test_zero_last_equity_returns_zero_percent() -> None:
    mapper = AccountPresentationMapper()

    result = mapper.map_account_section(
        make_account_data(
            equity=100000.0,
            last_equity=0.0,
        )
    )

    assert result.metrics.daily_change_percent == (
        "+0.00%"
    )


def test_position_is_formatted() -> None:
    mapper = AccountPresentationMapper()

    result = mapper.map_account_section(
        make_account_data(
            positions=(
                make_position(),
            )
        )
    )

    assert result.positions == (
        PositionRowViewModel(
            symbol="AAPL",
            side="Long",
            quantity="10",
            average_entry_price="$200.00",
            current_price="$205.00",
            market_value="$2,050.00",
            cost_basis="$2,000.00",
            unrealized_profit_loss="+$50.00",
            unrealized_profit_loss_percent="+2.50%",
        ),
    )


def test_fractional_quantity_is_preserved() -> None:
    mapper = AccountPresentationMapper()

    position = OpenPosition(
        symbol="AAPL",
        side="long",
        quantity=1.2345,
        average_entry_price=200.0,
        current_price=205.0,
        market_value=253.07,
        cost_basis=246.9,
        unrealized_profit_loss=6.17,
        unrealized_profit_loss_percent=0.025,
    )

    result = mapper.map_account_section(
        make_account_data(
            positions=(position,)
        )
    )

    assert result.positions[0].quantity == "1.2345"


def test_empty_positions_are_identified() -> None:
    mapper = AccountPresentationMapper()

    result = mapper.map_account_section(
        make_account_data()
    )

    assert result.positions == ()
    assert result.has_open_positions is False


def test_open_positions_are_identified() -> None:
    mapper = AccountPresentationMapper()

    result = mapper.map_account_section(
        make_account_data(
            positions=(
                make_position(),
            )
        )
    )

    assert result.has_open_positions is True


def test_trading_blocked_status() -> None:
    mapper = AccountPresentationMapper()

    result = mapper.map_account_section(
        make_account_data(
            trading_blocked=True,
        )
    )

    assert result.metrics.trading_status == (
        "Trading Blocked"
    )


def test_account_blocked_takes_priority() -> None:
    mapper = AccountPresentationMapper()

    result = mapper.map_account_section(
        make_account_data(
            trading_blocked=True,
            account_blocked=True,
        )
    )

    assert result.metrics.trading_status == (
        "Account Blocked"
    )


def test_zero_profit_is_formatted_as_positive_zero() -> None:
    mapper = AccountPresentationMapper()

    position = OpenPosition(
        symbol="MSFT",
        side="long",
        quantity=5.0,
        average_entry_price=400.0,
        current_price=400.0,
        market_value=2000.0,
        cost_basis=2000.0,
        unrealized_profit_loss=0.0,
        unrealized_profit_loss_percent=0.0,
    )

    result = mapper.map_account_section(
        make_account_data(
            positions=(position,)
        )
    )

    assert (
        result
        .positions[0]
        .unrealized_profit_loss
        == "+$0.00"
    )
    assert (
        result
        .positions[0]
        .unrealized_profit_loss_percent
        == "+0.00%"
    )