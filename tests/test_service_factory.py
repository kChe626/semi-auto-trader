from __future__ import annotations

from unittest.mock import Mock, patch

from dashboard.composition_service import (
    DashboardCompositionService,
)
from dashboard.service_factory import (
    create_dashboard_composition_service,
)


def make_factory_dependencies() -> dict[str, Mock]:
    return {
        "trading_client": Mock(
            name="trading-client"
        ),
        "trade_workflow": Mock(
            name="trade-workflow"
        ),
        "closed_trade_repository": Mock(
            name="closed-trade-repository"
        ),
        "performance_statistics": Mock(
            name="performance-statistics"
        ),
        "equity_curve": Mock(
            name="equity-curve"
        ),
        "drawdown_calculator": Mock(
            name="drawdown-calculator"
        ),
        "monthly_performance_calculator": Mock(
            name="monthly-performance-calculator"
        ),
        "yearly_performance_calculator": Mock(
            name="yearly-performance-calculator"
        ),
        "trade_distribution_calculator": Mock(
            name="trade-distribution-calculator"
        ),
    }


@patch("dashboard.service_factory.DashboardService")
@patch("dashboard.service_factory.AccountService")
def test_factory_returns_composition_service(
    account_service_class: Mock,
    dashboard_service_class: Mock,
) -> None:
    service = create_dashboard_composition_service(
        **make_factory_dependencies()
    )

    assert isinstance(
        service,
        DashboardCompositionService,
    )


@patch("dashboard.service_factory.DashboardService")
@patch("dashboard.service_factory.AccountService")
def test_factory_wires_account_service(
    account_service_class: Mock,
    dashboard_service_class: Mock,
) -> None:
    dependencies = make_factory_dependencies()

    create_dashboard_composition_service(
        **dependencies
    )

    account_service_class.assert_called_once_with(
        trading_client=dependencies[
            "trading_client"
        ],
    )


@patch("dashboard.service_factory.DashboardService")
@patch("dashboard.service_factory.AccountService")
def test_factory_wires_repository(
    account_service_class: Mock,
    dashboard_service_class: Mock,
) -> None:
    dependencies = make_factory_dependencies()

    create_dashboard_composition_service(
        **dependencies
    )

    dashboard_service_class.assert_called_once()

    call_kwargs = (
        dashboard_service_class
        .call_args
        .kwargs
    )

    assert (
        call_kwargs["closed_trade_repository"]
        is dependencies[
            "closed_trade_repository"
        ]
    )


@patch("dashboard.service_factory.DashboardService")
@patch("dashboard.service_factory.AccountService")
def test_factory_wires_all_analytics_calculators(
    account_service_class: Mock,
    dashboard_service_class: Mock,
) -> None:
    dependencies = make_factory_dependencies()

    create_dashboard_composition_service(
        **dependencies
    )

    dashboard_service_class.assert_called_once_with(
        closed_trade_repository=dependencies[
            "closed_trade_repository"
        ],
        performance_statistics=dependencies[
            "performance_statistics"
        ],
        equity_curve=dependencies[
            "equity_curve"
        ],
        drawdown_calculator=dependencies[
            "drawdown_calculator"
        ],
        monthly_performance_calculator=dependencies[
            "monthly_performance_calculator"
        ],
        yearly_performance_calculator=dependencies[
            "yearly_performance_calculator"
        ],
        trade_distribution_calculator=dependencies[
            "trade_distribution_calculator"
        ],
    )


@patch("dashboard.service_factory.scan_market")
@patch("dashboard.service_factory.DashboardService")
@patch("dashboard.service_factory.AccountService")
def test_factory_wires_scanner_and_workflow(
    account_service_class: Mock,
    dashboard_service_class: Mock,
    scan_market: Mock,
) -> None:
    dependencies = make_factory_dependencies()

    account_service = Mock(
        name="account-service"
    )
    analytics_service = Mock(
        name="analytics-service"
    )

    account_service_class.return_value = (
        account_service
    )
    dashboard_service_class.return_value = (
        analytics_service
    )

    service = create_dashboard_composition_service(
        **dependencies
    )

    assert (
        service._account_service
        is account_service
    )
    assert (
        service._scanner_loader
        is scan_market
    )
    assert (
        service._trade_workflow
        is dependencies["trade_workflow"]
    )
    assert (
        service._analytics_service
        is analytics_service
    )


@patch("dashboard.service_factory.scan_market")
@patch("dashboard.service_factory.DashboardService")
@patch("dashboard.service_factory.AccountService")
def test_factory_preserves_service_instances(
    account_service_class: Mock,
    dashboard_service_class: Mock,
    scan_market: Mock,
) -> None:
    dependencies = make_factory_dependencies()

    account_service = Mock(
        name="account-service"
    )
    analytics_service = Mock(
        name="analytics-service"
    )

    account_service_class.return_value = (
        account_service
    )
    dashboard_service_class.return_value = (
        analytics_service
    )

    service = create_dashboard_composition_service(
        **dependencies
    )

    assert (
        service._account_service
        is account_service
    )
    assert (
        service._trade_workflow
        is dependencies["trade_workflow"]
    )
    assert (
        service._analytics_service
        is analytics_service
    )


@patch("dashboard.service_factory.scan_market")
@patch("dashboard.service_factory.DashboardService")
@patch("dashboard.service_factory.AccountService")
def test_factory_does_not_load_data_during_creation(
    account_service_class: Mock,
    dashboard_service_class: Mock,
    scan_market: Mock,
) -> None:
    dependencies = make_factory_dependencies()

    account_service = Mock(
        name="account-service"
    )
    analytics_service = Mock(
        name="analytics-service"
    )

    account_service_class.return_value = (
        account_service
    )
    dashboard_service_class.return_value = (
        analytics_service
    )

    create_dashboard_composition_service(
        **dependencies
    )

    account_service.load_account_data\
        .assert_not_called()

    scan_market.assert_not_called()

    dependencies["trade_workflow"]\
        .prepare_trade\
        .assert_not_called()

    analytics_service.load_dashboard_data\
        .assert_not_called()