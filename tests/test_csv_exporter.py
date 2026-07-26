import csv
from datetime import (
    datetime,
    timedelta,
    timezone,
)
from pathlib import Path

import pytest

from models.closed_trade import ClosedTrade
from reporting.csv_exporter import (
    ClosedTradeCsvExporter,
)


def make_trade(
    *,
    trade_id: str,
    symbol: str = "AAPL",
    realized_pl: float = 250.0,
    r_multiple: float = 2.0,
) -> ClosedTrade:
    opened_at = datetime(
        2026,
        7,
        20,
        15,
        30,
        tzinfo=timezone.utc,
    )

    closed_at = (
        opened_at + timedelta(hours=2)
    )

    return ClosedTrade(
        trade_id=trade_id,
        symbol=symbol,
        entry_price=100.0,
        exit_price=105.0,
        quantity=10.0,
        realized_pl=realized_pl,
        r_multiple=r_multiple,
        holding_duration_seconds=7200.0,
        opened_at=opened_at,
        closed_at=closed_at,
    )


def read_csv_rows(
    path: Path,
) -> list[dict[str, str]]:
    with path.open(
        mode="r",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        return list(
            csv.DictReader(csv_file)
        )


def test_export_creates_csv_file(
    tmp_path: Path,
) -> None:
    output_path = (
        tmp_path / "closed_trades.csv"
    )

    result = ClosedTradeCsvExporter.export(
        [
            make_trade(
                trade_id="trade-1"
            )
        ],
        output_path,
    )

    assert result == output_path
    assert output_path.exists()
    assert output_path.is_file()


def test_export_writes_expected_headers(
    tmp_path: Path,
) -> None:
    output_path = (
        tmp_path / "closed_trades.csv"
    )

    ClosedTradeCsvExporter.export(
        [],
        output_path,
    )

    with output_path.open(
        mode="r",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        reader = csv.reader(csv_file)
        headers = next(reader)

    assert tuple(headers) == (
        ClosedTradeCsvExporter.FIELDNAMES
    )


def test_export_writes_trade_values(
    tmp_path: Path,
) -> None:
    trade = make_trade(
        trade_id="trade-1",
        symbol="NVDA",
        realized_pl=350.0,
        r_multiple=2.5,
    )

    output_path = (
        tmp_path / "closed_trades.csv"
    )

    ClosedTradeCsvExporter.export(
        [trade],
        output_path,
    )

    rows = read_csv_rows(
        output_path
    )

    assert len(rows) == 1

    row = rows[0]

    assert row["trade_id"] == "trade-1"
    assert row["symbol"] == "NVDA"
    assert float(
        row["entry_price"]
    ) == pytest.approx(100.0)

    assert float(
        row["exit_price"]
    ) == pytest.approx(105.0)

    assert float(
        row["quantity"]
    ) == pytest.approx(10.0)

    assert float(
        row["realized_pl"]
    ) == pytest.approx(350.0)

    assert float(
        row["r_multiple"]
    ) == pytest.approx(2.5)

    assert float(
        row["holding_duration_seconds"]
    ) == pytest.approx(7200.0)

    assert row["opened_at"] == (
        trade.opened_at.isoformat()
    )

    assert row["closed_at"] == (
        trade.closed_at.isoformat()
    )


def test_export_writes_multiple_trades(
    tmp_path: Path,
) -> None:
    trades = [
        make_trade(
            trade_id="trade-1",
            symbol="AAPL",
        ),
        make_trade(
            trade_id="trade-2",
            symbol="MSFT",
        ),
        make_trade(
            trade_id="trade-3",
            symbol="NVDA",
        ),
    ]

    output_path = (
        tmp_path / "closed_trades.csv"
    )

    ClosedTradeCsvExporter.export(
        trades,
        output_path,
    )

    rows = read_csv_rows(
        output_path
    )

    assert len(rows) == 3

    assert [
        row["trade_id"]
        for row in rows
    ] == [
        "trade-1",
        "trade-2",
        "trade-3",
    ]


def test_export_preserves_trade_order(
    tmp_path: Path,
) -> None:
    trades = [
        make_trade(
            trade_id="trade-3"
        ),
        make_trade(
            trade_id="trade-1"
        ),
        make_trade(
            trade_id="trade-2"
        ),
    ]

    output_path = (
        tmp_path / "closed_trades.csv"
    )

    ClosedTradeCsvExporter.export(
        trades,
        output_path,
    )

    rows = read_csv_rows(
        output_path
    )

    assert [
        row["trade_id"]
        for row in rows
    ] == [
        "trade-3",
        "trade-1",
        "trade-2",
    ]


def test_export_supports_generator_input(
    tmp_path: Path,
) -> None:
    trades = (
        make_trade(
            trade_id=f"trade-{index}"
        )
        for index in range(3)
    )

    output_path = (
        tmp_path / "closed_trades.csv"
    )

    ClosedTradeCsvExporter.export(
        trades,
        output_path,
    )

    rows = read_csv_rows(
        output_path
    )

    assert len(rows) == 3


def test_export_creates_parent_directories(
    tmp_path: Path,
) -> None:
    output_path = (
        tmp_path
        / "reports"
        / "history"
        / "closed_trades.csv"
    )

    ClosedTradeCsvExporter.export(
        [],
        output_path,
    )

    assert output_path.exists()


def test_export_overwrites_existing_file(
    tmp_path: Path,
) -> None:
    output_path = (
        tmp_path / "closed_trades.csv"
    )

    ClosedTradeCsvExporter.export(
        [
            make_trade(
                trade_id="old-trade"
            )
        ],
        output_path,
    )

    ClosedTradeCsvExporter.export(
        [
            make_trade(
                trade_id="new-trade"
            )
        ],
        output_path,
    )

    rows = read_csv_rows(
        output_path
    )

    assert len(rows) == 1
    assert rows[0]["trade_id"] == (
        "new-trade"
    )


def test_export_rejects_non_csv_extension(
    tmp_path: Path,
) -> None:
    output_path = (
        tmp_path / "closed_trades.txt"
    )

    with pytest.raises(
        ValueError,
        match=(
            "output_path must end with .csv"
        ),
    ):
        ClosedTradeCsvExporter.export(
            [],
            output_path,
        )


def test_export_rejects_invalid_trade_type(
    tmp_path: Path,
) -> None:
    output_path = (
        tmp_path / "closed_trades.csv"
    )

    with pytest.raises(
        TypeError,
        match=(
            "all trades must be "
            "ClosedTrade instances"
        ),
    ):
        ClosedTradeCsvExporter.export(
            [
                object(),
            ],  # type: ignore[list-item]
            output_path,
        )