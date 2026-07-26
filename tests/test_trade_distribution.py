from datetime import (
    datetime,
    timedelta,
    timezone,
)

import pytest

from analytics.trade_distribution import (
    TradeDistributionCalculator,
)
from models.closed_trade import ClosedTrade


def make_trade(
    *,
    trade_id: str,
    symbol: str,
    realized_pl: float,
    r_multiple: float,
    opened_at: datetime,
) -> ClosedTrade:
    closed_at = (
        opened_at + timedelta(hours=1)
    )

    return ClosedTrade(
        trade_id=trade_id,
        symbol=symbol,
        entry_price=100.0,
        exit_price=105.0,
        quantity=10.0,
        realized_pl=realized_pl,
        r_multiple=r_multiple,
        holding_duration_seconds=3600.0,
        opened_at=opened_at,
        closed_at=closed_at,
    )


def utc_datetime(
    year: int,
    month: int,
    day: int,
) -> datetime:
    return datetime(
        year,
        month,
        day,
        15,
        0,
        tzinfo=timezone.utc,
    )


def test_by_symbol_empty_trade_list() -> None:
    result = (
        TradeDistributionCalculator.by_symbol(
            []
        )
    )

    assert result == ()
    assert isinstance(result, tuple)


def test_by_weekday_empty_trade_list() -> None:
    result = (
        TradeDistributionCalculator.by_weekday(
            []
        )
    )

    assert result == ()
    assert isinstance(result, tuple)


def test_by_symbol_groups_trades() -> None:
    trades = [
        make_trade(
            trade_id="aapl-1",
            symbol="AAPL",
            realized_pl=200.0,
            r_multiple=2.0,
            opened_at=utc_datetime(
                2026,
                7,
                20,
            ),
        ),
        make_trade(
            trade_id="aapl-2",
            symbol="AAPL",
            realized_pl=-50.0,
            r_multiple=-0.5,
            opened_at=utc_datetime(
                2026,
                7,
                21,
            ),
        ),
        make_trade(
            trade_id="nvda-1",
            symbol="NVDA",
            realized_pl=300.0,
            r_multiple=3.0,
            opened_at=utc_datetime(
                2026,
                7,
                22,
            ),
        ),
    ]

    result = (
        TradeDistributionCalculator.by_symbol(
            trades
        )
    )

    assert [
        distribution.group
        for distribution in result
    ] == [
        "AAPL",
        "NVDA",
    ]

    assert result[0].trade_count == 2
    assert result[0].net_realized_pl == (
        pytest.approx(150.0)
    )

    assert result[1].trade_count == 1
    assert result[1].net_realized_pl == (
        pytest.approx(300.0)
    )


def test_by_symbol_calculates_metrics() -> None:
    trades = [
        make_trade(
            trade_id="trade-1",
            symbol="AAPL",
            realized_pl=300.0,
            r_multiple=2.0,
            opened_at=utc_datetime(
                2026,
                7,
                20,
            ),
        ),
        make_trade(
            trade_id="trade-2",
            symbol="AAPL",
            realized_pl=-100.0,
            r_multiple=-1.0,
            opened_at=utc_datetime(
                2026,
                7,
                21,
            ),
        ),
        make_trade(
            trade_id="trade-3",
            symbol="AAPL",
            realized_pl=200.0,
            r_multiple=1.5,
            opened_at=utc_datetime(
                2026,
                7,
                22,
            ),
        ),
        make_trade(
            trade_id="trade-4",
            symbol="AAPL",
            realized_pl=0.0,
            r_multiple=0.0,
            opened_at=utc_datetime(
                2026,
                7,
                23,
            ),
        ),
    ]

    result = (
        TradeDistributionCalculator.by_symbol(
            trades
        )
    )

    distribution = result[0]

    assert distribution.group == "AAPL"
    assert distribution.trade_count == 4
    assert distribution.winning_trades == 2
    assert distribution.losing_trades == 1
    assert distribution.breakeven_trades == 1

    assert distribution.win_rate == (
        pytest.approx(0.5)
    )

    assert distribution.net_realized_pl == (
        pytest.approx(400.0)
    )

    assert distribution.gross_profit == (
        pytest.approx(500.0)
    )

    assert distribution.gross_loss == (
        pytest.approx(-100.0)
    )

    assert distribution.average_trade == (
        pytest.approx(100.0)
    )

    assert distribution.average_winner == (
        pytest.approx(250.0)
    )

    assert distribution.average_loser == (
        pytest.approx(-100.0)
    )

    assert distribution.profit_factor == (
        pytest.approx(5.0)
    )

    assert distribution.total_r_multiple == (
        pytest.approx(2.5)
    )

    assert distribution.average_r_multiple == (
        pytest.approx(0.625)
    )

    assert distribution.best_trade_pl == (
        pytest.approx(300.0)
    )

    assert distribution.worst_trade_pl == (
        pytest.approx(-100.0)
    )


def test_by_symbol_results_are_alphabetical() -> None:
    trades = [
        make_trade(
            trade_id="tsla",
            symbol="TSLA",
            realized_pl=100.0,
            r_multiple=1.0,
            opened_at=utc_datetime(
                2026,
                7,
                20,
            ),
        ),
        make_trade(
            trade_id="aapl",
            symbol="AAPL",
            realized_pl=100.0,
            r_multiple=1.0,
            opened_at=utc_datetime(
                2026,
                7,
                20,
            ),
        ),
        make_trade(
            trade_id="nvda",
            symbol="NVDA",
            realized_pl=100.0,
            r_multiple=1.0,
            opened_at=utc_datetime(
                2026,
                7,
                20,
            ),
        ),
    ]

    result = (
        TradeDistributionCalculator.by_symbol(
            trades
        )
    )

    assert [
        distribution.group
        for distribution in result
    ] == [
        "AAPL",
        "NVDA",
        "TSLA",
    ]


def test_by_weekday_groups_using_opened_at() -> None:
    trades = [
        make_trade(
            trade_id="monday-1",
            symbol="AAPL",
            realized_pl=100.0,
            r_multiple=1.0,
            opened_at=utc_datetime(
                2026,
                7,
                20,
            ),
        ),
        make_trade(
            trade_id="monday-2",
            symbol="NVDA",
            realized_pl=200.0,
            r_multiple=2.0,
            opened_at=utc_datetime(
                2026,
                7,
                20,
            ),
        ),
        make_trade(
            trade_id="tuesday-1",
            symbol="MSFT",
            realized_pl=-50.0,
            r_multiple=-0.5,
            opened_at=utc_datetime(
                2026,
                7,
                21,
            ),
        ),
    ]

    result = (
        TradeDistributionCalculator.by_weekday(
            trades
        )
    )

    assert [
        distribution.group
        for distribution in result
    ] == [
        "Monday",
        "Tuesday",
    ]

    assert result[0].trade_count == 2
    assert result[0].net_realized_pl == (
        pytest.approx(300.0)
    )

    assert result[1].trade_count == 1
    assert result[1].net_realized_pl == (
        pytest.approx(-50.0)
    )


def test_by_weekday_results_follow_calendar_order() -> None:
    trades = [
        make_trade(
            trade_id="friday",
            symbol="AAPL",
            realized_pl=100.0,
            r_multiple=1.0,
            opened_at=utc_datetime(
                2026,
                7,
                24,
            ),
        ),
        make_trade(
            trade_id="monday",
            symbol="AAPL",
            realized_pl=100.0,
            r_multiple=1.0,
            opened_at=utc_datetime(
                2026,
                7,
                20,
            ),
        ),
        make_trade(
            trade_id="wednesday",
            symbol="AAPL",
            realized_pl=100.0,
            r_multiple=1.0,
            opened_at=utc_datetime(
                2026,
                7,
                22,
            ),
        ),
    ]

    result = (
        TradeDistributionCalculator.by_weekday(
            trades
        )
    )

    assert [
        distribution.group
        for distribution in result
    ] == [
        "Monday",
        "Wednesday",
        "Friday",
    ]


def test_all_winning_group_has_none_profit_factor() -> None:
    trades = [
        make_trade(
            trade_id="trade-1",
            symbol="AAPL",
            realized_pl=100.0,
            r_multiple=1.0,
            opened_at=utc_datetime(
                2026,
                7,
                20,
            ),
        ),
        make_trade(
            trade_id="trade-2",
            symbol="AAPL",
            realized_pl=200.0,
            r_multiple=2.0,
            opened_at=utc_datetime(
                2026,
                7,
                21,
            ),
        ),
    ]

    result = (
        TradeDistributionCalculator.by_symbol(
            trades
        )
    )

    assert result[0].profit_factor is None


def test_all_losing_group_has_zero_profit_factor() -> None:
    trades = [
        make_trade(
            trade_id="trade-1",
            symbol="AAPL",
            realized_pl=-100.0,
            r_multiple=-1.0,
            opened_at=utc_datetime(
                2026,
                7,
                20,
            ),
        ),
        make_trade(
            trade_id="trade-2",
            symbol="AAPL",
            realized_pl=-200.0,
            r_multiple=-2.0,
            opened_at=utc_datetime(
                2026,
                7,
                21,
            ),
        ),
    ]

    result = (
        TradeDistributionCalculator.by_symbol(
            trades
        )
    )

    assert result[0].profit_factor == (
        pytest.approx(0.0)
    )


def test_all_breakeven_group_has_zero_profit_factor() -> None:
    trades = [
        make_trade(
            trade_id="trade-1",
            symbol="AAPL",
            realized_pl=0.0,
            r_multiple=0.0,
            opened_at=utc_datetime(
                2026,
                7,
                20,
            ),
        ),
        make_trade(
            trade_id="trade-2",
            symbol="AAPL",
            realized_pl=0.0,
            r_multiple=0.0,
            opened_at=utc_datetime(
                2026,
                7,
                21,
            ),
        ),
    ]

    result = (
        TradeDistributionCalculator.by_symbol(
            trades
        )
    )

    assert result[0].profit_factor == (
        pytest.approx(0.0)
    )


def test_generator_input_is_supported() -> None:
    trades = (
        make_trade(
            trade_id=f"trade-{index}",
            symbol="AAPL",
            realized_pl=100.0,
            r_multiple=1.0,
            opened_at=utc_datetime(
                2026,
                7,
                20 + index,
            ),
        )
        for index in range(3)
    )

    result = (
        TradeDistributionCalculator.by_symbol(
            trades
        )
    )

    assert len(result) == 1
    assert result[0].trade_count == 3


@pytest.mark.parametrize(
    "method_name",
    [
        "by_symbol",
        "by_weekday",
    ],
)
def test_invalid_trade_type_is_rejected(
    method_name: str,
) -> None:
    method = getattr(
        TradeDistributionCalculator,
        method_name,
    )

    with pytest.raises(
        TypeError,
        match=(
            "all trades must be "
            "ClosedTrade instances"
        ),
    ):
        method(
            [
                object(),
            ]
        )