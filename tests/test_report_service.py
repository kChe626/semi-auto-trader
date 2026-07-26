import csv
from datetime import (
    datetime,
    timedelta,
    timezone,
)
from pathlib import Path
from unittest.mock import Mock

import pytest

from models.closed_trade import ClosedTrade
from reporting.report_service import (
    ClosedTradeReportService,
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


def read_rows(
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


def test_service_loads_and_exports_trades(
    tmp_path: Path,
) -> None:
    trades = [
        make_trade(
            trade_id="trade-1",
            symbol="AAPL",
        ),
        make_trade(
            trade_id="trade-2",
            symbol="NVDA",
        ),
    ]

    loader = Mock(
        return_value=trades
    )

    service = ClosedTradeReportService(
        loader
    )

    output_path = (
        tmp_path / "closed_trades.csv"
    )

    result = service.export_csv(
        output_path
    )

    assert result == output_path
    assert output_path.exists()

    loader.assert_called_once_with()

    rows = read_rows(
        output_path
    )

    assert len(rows) == 2

    assert [
        row["trade_id"]
        for row in rows
    ] == [
        "trade-1",
        "trade-2",
    ]


def test_service_exports_empty_report(
    tmp_path: Path,
) -> None:
    loader = Mock(
        return_value=[]
    )

    service = ClosedTradeReportService(
        loader
    )

    output_path = (
        tmp_path / "closed_trades.csv"
    )

    service.export_csv(
        output_path
    )

    assert output_path.exists()

    rows = read_rows(
        output_path
    )

    assert rows == []


def test_service_supports_generator_loader(
    tmp_path: Path,
) -> None:
    def load_trades():
        return (
            make_trade(
                trade_id=f"trade-{index}"
            )
            for index in range(3)
        )

    service = ClosedTradeReportService(
        load_trades
    )

    output_path = (
        tmp_path / "closed_trades.csv"
    )

    service.export_csv(
        output_path
    )

    rows = read_rows(
        output_path
    )

    assert len(rows) == 3


def test_service_creates_parent_directories(
    tmp_path: Path,
) -> None:
    service = ClosedTradeReportService(
        lambda: []
    )

    output_path = (
        tmp_path
        / "reports"
        / "history"
        / "closed_trades.csv"
    )

    service.export_csv(
        output_path
    )

    assert output_path.exists()


def test_service_returns_exported_path(
    tmp_path: Path,
) -> None:
    service = ClosedTradeReportService(
        lambda: []
    )

    output_path = (
        tmp_path / "closed_trades.csv"
    )

    result = service.export_csv(
        output_path
    )

    assert isinstance(result, Path)
    assert result == output_path


def test_service_propagates_loader_failure(
    tmp_path: Path,
) -> None:
    def failing_loader():
        raise RuntimeError(
            "repository unavailable"
        )

    service = ClosedTradeReportService(
        failing_loader
    )

    with pytest.raises(
        RuntimeError,
        match="repository unavailable",
    ):
        service.export_csv(
            tmp_path / "closed_trades.csv"
        )


def test_service_rejects_invalid_loader() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "load_closed_trades "
            "must be callable"
        ),
    ):
        ClosedTradeReportService(
            object()  # type: ignore[arg-type]
        )


def test_service_rejects_invalid_trade_data(
    tmp_path: Path,
) -> None:
    service = ClosedTradeReportService(
        lambda: [
            object(),
        ]  # type: ignore[list-item]
    )

    with pytest.raises(
        TypeError,
        match=(
            "all trades must be "
            "ClosedTrade instances"
        ),
    ):
        service.export_csv(
            tmp_path / "closed_trades.csv"
        )


def test_service_rejects_non_csv_path(
    tmp_path: Path,
) -> None:
    service = ClosedTradeReportService(
        lambda: []
    )

    with pytest.raises(
        ValueError,
        match=(
            "output_path must end with .csv"
        ),
    ):
        service.export_csv(
            tmp_path / "closed_trades.txt"
        )


def test_each_export_loads_fresh_data(
    tmp_path: Path,
) -> None:
    loader = Mock(
        side_effect=[
            [
                make_trade(
                    trade_id="trade-1"
                )
            ],
            [
                make_trade(
                    trade_id="trade-2"
                )
            ],
        ]
    )

    service = ClosedTradeReportService(
        loader
    )

    output_path = (
        tmp_path / "closed_trades.csv"
    )

    service.export_csv(
        output_path
    )

    first_rows = read_rows(
        output_path
    )

    service.export_csv(
        output_path
    )

    second_rows = read_rows(
        output_path
    )

    assert first_rows[0]["trade_id"] == (
        "trade-1"
    )

    assert second_rows[0]["trade_id"] == (
        "trade-2"
    )

    assert loader.call_count == 2