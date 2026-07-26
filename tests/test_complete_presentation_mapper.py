from __future__ import annotations

from unittest.mock import Mock

import pytest

from dashboard.complete_presentation_mapper import (
    CompleteDashboardPresentationMapper,
)
from dashboard.complete_presentation_models import (
    CompleteDashboardViewModel,
)
from dashboard.composition_service import (
    CompleteDashboardData,
)


def make_mapper(
    *,
    account_mapper: Mock | None = None,
    analytics_mapper: Mock | None = None,
) -> tuple[
    CompleteDashboardPresentationMapper,
    Mock,
    Mock,
]:
    account_mapper = account_mapper or Mock()
    analytics_mapper = analytics_mapper or Mock()

    mapper = CompleteDashboardPresentationMapper(
        account_mapper=account_mapper,
        analytics_mapper=analytics_mapper,
    )

    return (
        mapper,
        account_mapper,
        analytics_mapper,
    )


def make_dashboard_data() -> CompleteDashboardData:
    return CompleteDashboardData(
        account_data=Mock(name="account-data"),
        analytics_data=Mock(name="analytics-data"),
    )


def test_map_dashboard_returns_complete_view_model() -> None:
    (
        mapper,
        account_mapper,
        analytics_mapper,
    ) = make_mapper()

    account_view_model = Mock(
        name="account-view-model"
    )
    analytics_view_model = Mock(
        name="analytics-view-model"
    )

    account_mapper.map_account_section.return_value = (
        account_view_model
    )
    analytics_mapper\
        .map_analytics_section.return_value = (
            analytics_view_model
        )

    result = mapper.map_dashboard(
        make_dashboard_data()
    )

    assert isinstance(
        result,
        CompleteDashboardViewModel,
    )
    assert result.account is account_view_model
    assert result.analytics is analytics_view_model


def test_account_mapper_receives_account_data() -> None:
    (
        mapper,
        account_mapper,
        _,
    ) = make_mapper()

    dashboard_data = make_dashboard_data()

    mapper.map_dashboard(dashboard_data)

    account_mapper.map_account_section\
        .assert_called_once_with(
            dashboard_data.account_data
        )


def test_analytics_mapper_receives_analytics_data() -> None:
    (
        mapper,
        _,
        analytics_mapper,
    ) = make_mapper()

    dashboard_data = make_dashboard_data()

    mapper.map_dashboard(dashboard_data)

    analytics_mapper.map_analytics_section\
        .assert_called_once_with(
            dashboard_data.analytics_data
        )


def test_account_is_mapped_before_analytics() -> None:
    calls: list[str] = []

    account_mapper = Mock()
    analytics_mapper = Mock()

    account_mapper.map_account_section.side_effect = (
        lambda _: calls.append("account") or Mock()
    )

    analytics_mapper.map_analytics_section.side_effect = (
        lambda _: calls.append("analytics") or Mock()
    )

    mapper = CompleteDashboardPresentationMapper(
        account_mapper=account_mapper,
        analytics_mapper=analytics_mapper,
    )

    mapper.map_dashboard(
        make_dashboard_data()
    )

    assert calls == [
        "account",
        "analytics",
    ]


def test_account_mapper_exception_is_not_hidden() -> None:
    (
        mapper,
        account_mapper,
        analytics_mapper,
    ) = make_mapper()

    account_mapper.map_account_section.side_effect = (
        RuntimeError("account mapping failed")
    )

    with pytest.raises(
        RuntimeError,
        match="account mapping failed",
    ):
        mapper.map_dashboard(
            make_dashboard_data()
        )

    analytics_mapper.map_analytics_section\
        .assert_not_called()


def test_analytics_mapper_exception_is_not_hidden() -> None:
    (
        mapper,
        account_mapper,
        analytics_mapper,
    ) = make_mapper()

    account_mapper.map_account_section.return_value = (
        Mock()
    )

    analytics_mapper.map_analytics_section.side_effect = (
        RuntimeError("analytics mapping failed")
    )

    with pytest.raises(
        RuntimeError,
        match="analytics mapping failed",
    ):
        mapper.map_dashboard(
            make_dashboard_data()
        )

    account_mapper.map_account_section\
        .assert_called_once()


def test_each_mapping_returns_new_view_model() -> None:
    (
        mapper,
        account_mapper,
        analytics_mapper,
    ) = make_mapper()

    account_mapper.map_account_section.return_value = (
        Mock()
    )
    analytics_mapper\
        .map_analytics_section.return_value = (
            Mock()
        )

    dashboard_data = make_dashboard_data()

    first_result = mapper.map_dashboard(
        dashboard_data
    )
    second_result = mapper.map_dashboard(
        dashboard_data
    )

    assert first_result is not second_result
    assert (
        account_mapper
        .map_account_section
        .call_count
        == 2
    )
    assert (
        analytics_mapper
        .map_analytics_section
        .call_count
        == 2
    )