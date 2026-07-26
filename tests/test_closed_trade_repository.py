from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from database.closed_trade_repository import (
    ClosedTradeRepository,
)


OPENED_AT = datetime(
    2026,
    7,
    21,
    13,
    0,
    tzinfo=timezone.utc,
)

CLOSED_AT = OPENED_AT + timedelta(hours=2)


class FakeClosedTradeEventSource:
    def __init__(
        self,
        events: list[dict[str, Any]],
    ) -> None:
        self.events = events
        self.call_count = 0

    def get_closed_trade_events(
        self,
    ) -> list[dict[str, Any]]:
        self.call_count += 1
        return self.events


def make_event(
    **overrides: Any,
) -> dict[str, Any]:
    event: dict[str, Any] = {
        "trade_id": "trade-1",
        "symbol": "AAPL",
        "entry_price": 200.0,
        "exit_price": 210.0,
        "quantity": 10.0,
        "realized_pl": 100.0,
        "r_multiple": 2.0,
        "holding_duration_seconds": 7200.0,
        "opened_at": OPENED_AT.isoformat(),
        "closed_at": CLOSED_AT.isoformat(),
    }

    event.update(overrides)

    return event


def test_get_all_reads_event_source() -> None:
    source = FakeClosedTradeEventSource(
        [make_event()]
    )

    repository = ClosedTradeRepository(source)

    trades = repository.get_all()

    assert source.call_count == 1
    assert len(trades) == 1


def test_get_all_maps_event_to_closed_trade() -> None:
    source = FakeClosedTradeEventSource(
        [make_event()]
    )

    repository = ClosedTradeRepository(source)

    trade = repository.get_all()[0]

    assert trade.trade_id == "trade-1"
    assert trade.symbol == "AAPL"
    assert trade.entry_price == pytest.approx(
        200.0
    )
    assert trade.exit_price == pytest.approx(
        210.0
    )
    assert trade.quantity == pytest.approx(
        10.0
    )
    assert trade.realized_pl == pytest.approx(
        100.0
    )
    assert trade.r_multiple == pytest.approx(
        2.0
    )
    assert (
        trade.holding_duration_seconds
        == pytest.approx(7200.0)
    )
    assert trade.opened_at == OPENED_AT
    assert trade.closed_at == CLOSED_AT


def test_get_all_returns_multiple_trades() -> None:
    source = FakeClosedTradeEventSource(
        [
            make_event(
                trade_id="trade-1",
                symbol="AAPL",
            ),
            make_event(
                trade_id="trade-2",
                symbol="MSFT",
            ),
        ]
    )

    repository = ClosedTradeRepository(source)

    trades = repository.get_all()

    assert len(trades) == 2
    assert trades[0].trade_id == "trade-1"
    assert trades[1].trade_id == "trade-2"


def test_get_all_returns_empty_list() -> None:
    source = FakeClosedTradeEventSource([])

    repository = ClosedTradeRepository(source)

    assert repository.get_all() == []


def test_from_events_accepts_generator() -> None:
    events = (
        make_event(
            trade_id=f"trade-{index}",
        )
        for index in range(3)
    )

    trades = ClosedTradeRepository.from_events(
        events
    )

    assert len(trades) == 3


def test_numeric_strings_are_converted() -> None:
    source = FakeClosedTradeEventSource(
        [
            make_event(
                entry_price="200.00",
                exit_price="210.00",
                quantity="10",
                realized_pl="100.00",
                r_multiple="2.0",
                holding_duration_seconds="7200",
            )
        ]
    )

    trade = ClosedTradeRepository(
        source
    ).get_all()[0]

    assert trade.entry_price == pytest.approx(
        200.0
    )
    assert trade.realized_pl == pytest.approx(
        100.0
    )


def test_datetime_objects_are_accepted() -> None:
    source = FakeClosedTradeEventSource(
        [
            make_event(
                opened_at=OPENED_AT,
                closed_at=CLOSED_AT,
            )
        ]
    )

    trade = ClosedTradeRepository(
        source
    ).get_all()[0]

    assert trade.opened_at == OPENED_AT
    assert trade.closed_at == CLOSED_AT


def test_identity_fields_are_normalized() -> None:
    source = FakeClosedTradeEventSource(
        [
            make_event(
                trade_id="  trade-1  ",
                symbol=" aapl ",
            )
        ]
    )

    trade = ClosedTradeRepository(
        source
    ).get_all()[0]

    assert trade.trade_id == "trade-1"
    assert trade.symbol == "AAPL"


@pytest.mark.parametrize(
    "field_name",
    [
        "trade_id",
        "symbol",
        "entry_price",
        "exit_price",
        "quantity",
        "realized_pl",
        "r_multiple",
        "holding_duration_seconds",
        "opened_at",
        "closed_at",
    ],
)
def test_missing_required_field_is_rejected(
    field_name: str,
) -> None:
    event = make_event()
    del event[field_name]

    with pytest.raises(
        ValueError,
        match=(
            f"closed trade event is missing "
            f"{field_name}"
        ),
    ):
        ClosedTradeRepository.from_events(
            [event]
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "trade_id",
        "symbol",
        "entry_price",
        "exit_price",
        "quantity",
        "realized_pl",
        "r_multiple",
        "holding_duration_seconds",
        "opened_at",
        "closed_at",
    ],
)
def test_none_required_field_is_rejected(
    field_name: str,
) -> None:
    event = make_event(
        **{field_name: None}
    )

    with pytest.raises(
        ValueError,
        match=(
            f"closed trade event has no "
            f"{field_name}"
        ),
    ):
        ClosedTradeRepository.from_events(
            [event]
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "entry_price",
        "exit_price",
        "quantity",
        "realized_pl",
        "r_multiple",
        "holding_duration_seconds",
    ],
)
def test_invalid_numeric_field_is_rejected(
    field_name: str,
) -> None:
    event = make_event(
        **{field_name: "not-a-number"}
    )

    with pytest.raises(
        ValueError,
        match=(
            f"closed trade event has invalid "
            f"{field_name}"
        ),
    ):
        ClosedTradeRepository.from_events(
            [event]
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "opened_at",
        "closed_at",
    ],
)
def test_invalid_datetime_is_rejected(
    field_name: str,
) -> None:
    event = make_event(
        **{field_name: "invalid-date"}
    )

    with pytest.raises(
        ValueError,
        match=(
            f"closed trade event has invalid "
            f"{field_name}"
        ),
    ):
        ClosedTradeRepository.from_events(
            [event]
        )