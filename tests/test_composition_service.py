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


def test_load_complete_dashboard_data_returns_snapshot() -> None:
    account_service = Mock()
    analytics_service = Mock()

    account_data = make_account_data()

    analytics_data = Mock(
        name="analytics-data"
    )

    account_service.load_account_data.return_value = (
        account_data
    )

    analytics_service.load_dashboard_data.return_value = (
        analytics_data
    )

    service = DashboardCompositionService(
        account_service=account_service,
        analytics_service=analytics_service,
    )

    result = service.load_complete_dashboard_data()

    assert isinstance(
        result,
        CompleteDashboardData,
    )

    assert result.account_data is account_data
    assert result.analytics_data is analytics_data


def test_account_service_is_called_once() -> None:
    account_service = Mock()
    analytics_service = Mock()

    account_service.load_account_data.return_value = (
        make_account_data()
    )

    service = DashboardCompositionService(
        account_service=account_service,
        analytics_service=analytics_service,
    )

    service.load_complete_dashboard_data()

    account_service.load_account_data\
        .assert_called_once_with()


def test_analytics_service_is_called_once() -> None:
    account_service = Mock()
    analytics_service = Mock()

    account_service.load_account_data.return_value = (
        make_account_data()
    )

    service = DashboardCompositionService(
        account_service=account_service,
        analytics_service=analytics_service,
    )

    service.load_complete_dashboard_data()

    analytics_service.load_dashboard_data\
        .assert_called_once_with(
            starting_equity=ACCOUNT_EQUITY,
        )


def test_account_data_is_loaded_before_analytics() -> None:
    calls: list[str] = []

    account_service = Mock()
    analytics_service = Mock()

    account_data = make_account_data()

    def load_account_data() -> Mock:
        calls.append("account")

        return account_data

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

    analytics_service.load_dashboard_data.side_effect = (
        load_dashboard_data
    )

    service = DashboardCompositionService(
        account_service=account_service,
        analytics_service=analytics_service,
    )

    service.load_complete_dashboard_data()

    assert calls == [
        "account",
        "analytics",
    ]


def test_account_exception_is_not_hidden() -> None:
    account_service = Mock()
    analytics_service = Mock()

    account_service.load_account_data.side_effect = (
        RuntimeError("account unavailable")
    )

    service = DashboardCompositionService(
        account_service=account_service,
        analytics_service=analytics_service,
    )

    with pytest.raises(
        RuntimeError,
        match="account unavailable",
    ):
        service.load_complete_dashboard_data()

    analytics_service.load_dashboard_data\
        .assert_not_called()


def test_analytics_exception_is_not_hidden() -> None:
    account_service = Mock()
    analytics_service = Mock()

    account_service.load_account_data.return_value = (
        make_account_data()
    )

    analytics_service.load_dashboard_data.side_effect = (
        RuntimeError("analytics unavailable")
    )

    service = DashboardCompositionService(
        account_service=account_service,
        analytics_service=analytics_service,
    )

    with pytest.raises(
        RuntimeError,
        match="analytics unavailable",
    ):
        service.load_complete_dashboard_data()

    account_service.load_account_data\
        .assert_called_once_with()


def test_each_load_returns_new_snapshot() -> None:
    account_service = Mock()
    analytics_service = Mock()

    account_service.load_account_data.return_value = (
        make_account_data()
    )

    service = DashboardCompositionService(
        account_service=account_service,
        analytics_service=analytics_service,
    )

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