from __future__ import annotations

from unittest.mock import Mock

import pytest

from dashboard.composition_service import (
    CompleteDashboardData,
    DashboardCompositionService,
)


ACCOUNT_EQUITY = 100_000.0


def make_account_data() -> Mock:
    account_data = Mock(name="account-data")

    account_data.account.equity = (
        ACCOUNT_EQUITY
    )

    return account_data


def make_service(
    *,
    account_service: Mock | None = None,
    scanner_loader: Mock | None = None,
    analytics_service: Mock | None = None,
) -> tuple[
    DashboardCompositionService,
    Mock,
    Mock,
    Mock,
]:
    account_service = account_service or Mock()
    scanner_loader = scanner_loader or Mock()
    analytics_service = analytics_service or Mock()

    account_service.load_account_data.return_value = (
        make_account_data()
    )

    scanner_loader.return_value = []

    service = DashboardCompositionService(
        account_service=account_service,
        scanner_loader=scanner_loader,
        analytics_service=analytics_service,
    )

    return (
        service,
        account_service,
        scanner_loader,
        analytics_service,
    )


def test_load_complete_dashboard_data_returns_snapshot() -> None:
    (
        service,
        account_service,
        scanner_loader,
        analytics_service,
    ) = make_service()

    account_data = make_account_data()
    scanner_signals = [
        Mock(name="signal-one"),
        Mock(name="signal-two"),
    ]
    analytics_data = Mock(
        name="analytics-data"
    )

    account_service.load_account_data.return_value = (
        account_data
    )
    scanner_loader.return_value = scanner_signals
    analytics_service.load_dashboard_data.return_value = (
        analytics_data
    )

    result = service.load_complete_dashboard_data()

    assert isinstance(
        result,
        CompleteDashboardData,
    )

    assert result.account_data is account_data
    assert result.scanner_signals == tuple(
        scanner_signals
    )
    assert result.analytics_data is analytics_data


def test_account_service_is_called_once() -> None:
    (
        service,
        account_service,
        _,
        _,
    ) = make_service()

    service.load_complete_dashboard_data()

    account_service.load_account_data\
        .assert_called_once_with()


def test_scanner_loader_is_called_once() -> None:
    (
        service,
        _,
        scanner_loader,
        _,
    ) = make_service()

    service.load_complete_dashboard_data()

    scanner_loader.assert_called_once_with()


def test_analytics_service_is_called_once() -> None:
    (
        service,
        _,
        _,
        analytics_service,
    ) = make_service()

    service.load_complete_dashboard_data()

    analytics_service.load_dashboard_data\
        .assert_called_once_with(
            starting_equity=ACCOUNT_EQUITY,
        )


def test_services_are_loaded_in_expected_order() -> None:
    calls: list[str] = []

    account_service = Mock()
    scanner_loader = Mock()
    analytics_service = Mock()

    account_data = make_account_data()

    def load_account_data() -> Mock:
        calls.append("account")

        return account_data

    def load_scanner_signals() -> list[Mock]:
        calls.append("scanner")

        return []

    def load_dashboard_data(
        *,
        starting_equity: float,
    ) -> Mock:
        assert starting_equity == ACCOUNT_EQUITY

        calls.append("analytics")

        return Mock(name="analytics-data")

    account_service.load_account_data.side_effect = (
        load_account_data
    )
    scanner_loader.side_effect = (
        load_scanner_signals
    )
    analytics_service.load_dashboard_data.side_effect = (
        load_dashboard_data
    )

    service = DashboardCompositionService(
        account_service=account_service,
        scanner_loader=scanner_loader,
        analytics_service=analytics_service,
    )

    service.load_complete_dashboard_data()

    assert calls == [
        "account",
        "scanner",
        "analytics",
    ]


def test_scanner_generator_is_materialized_once() -> None:
    (
        service,
        _,
        scanner_loader,
        _,
    ) = make_service()

    signals = (
        Mock(name=f"signal-{index}")
        for index in range(2)
    )

    scanner_loader.return_value = signals

    result = service.load_complete_dashboard_data()

    assert len(result.scanner_signals) == 2
    assert scanner_loader.call_count == 1


def test_account_exception_is_not_hidden() -> None:
    (
        service,
        account_service,
        scanner_loader,
        analytics_service,
    ) = make_service()

    account_service.load_account_data.side_effect = (
        RuntimeError("account unavailable")
    )

    with pytest.raises(
        RuntimeError,
        match="account unavailable",
    ):
        service.load_complete_dashboard_data()

    scanner_loader.assert_not_called()

    analytics_service.load_dashboard_data\
        .assert_not_called()


def test_scanner_exception_is_not_hidden() -> None:
    (
        service,
        account_service,
        scanner_loader,
        analytics_service,
    ) = make_service()

    scanner_loader.side_effect = RuntimeError(
        "scanner unavailable"
    )

    with pytest.raises(
        RuntimeError,
        match="scanner unavailable",
    ):
        service.load_complete_dashboard_data()

    account_service.load_account_data\
        .assert_called_once_with()

    analytics_service.load_dashboard_data\
        .assert_not_called()


def test_analytics_exception_is_not_hidden() -> None:
    (
        service,
        account_service,
        scanner_loader,
        analytics_service,
    ) = make_service()

    analytics_service.load_dashboard_data.side_effect = (
        RuntimeError("analytics unavailable")
    )

    with pytest.raises(
        RuntimeError,
        match="analytics unavailable",
    ):
        service.load_complete_dashboard_data()

    account_service.load_account_data\
        .assert_called_once_with()

    scanner_loader.assert_called_once_with()


def test_each_load_returns_new_snapshot() -> None:
    (
        service,
        account_service,
        scanner_loader,
        analytics_service,
    ) = make_service()

    first_result = (
        service.load_complete_dashboard_data()
    )

    second_result = (
        service.load_complete_dashboard_data()
    )

    assert first_result is not second_result

    assert (
        account_service.load_account_data.call_count
        == 2
    )

    assert scanner_loader.call_count == 2

    assert (
        analytics_service.load_dashboard_data.call_count
        == 2
    )

    assert (
        analytics_service
        .load_dashboard_data.call_args_list[0]
        .kwargs["starting_equity"]
        == ACCOUNT_EQUITY
    )

    assert (
        analytics_service
        .load_dashboard_data.call_args_list[1]
        .kwargs["starting_equity"]
        == ACCOUNT_EQUITY
    )