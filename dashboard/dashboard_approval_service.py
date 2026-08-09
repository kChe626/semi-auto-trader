from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from typing import Any, Protocol

from config.trading_config import (
    EXECUTION_ENABLED,
    MAX_APPROVAL_AGE_MINUTES,
)
from models.preflight_result import PreflightResult
from models.trade_plan import TradePlan
from models.workflow_result import WorkflowResult
from trade_management.trade_identity import (
    create_trade_id,
)


class TradeExecutorProtocol(Protocol):
    def execute(
        self,
        workflow: WorkflowResult,
    ) -> Any:
        ...


class PortfolioManagerProtocol(Protocol):
    def can_open_new_trade(
        self,
    ) -> tuple[bool, str]:
        ...


class PreflightRunnerProtocol(Protocol):
    def __call__(
        self,
        plan: TradePlan,
    ) -> PreflightResult:
        ...


class DashboardApprovalService:
    """
    Approve and execute dashboard trade workflows.

    Execution is protected by:
    - workflow readiness
    - the execution-enabled switch
    - candidate freshness
    - a fresh portfolio-level risk check
    - a fresh broker preflight check
    """

    def __init__(
        self,
        *,
        trade_executor: TradeExecutorProtocol,
        portfolio_manager: PortfolioManagerProtocol,
        preflight_runner: PreflightRunnerProtocol,
    ) -> None:
        self._trade_executor = trade_executor
        self._portfolio_manager = portfolio_manager
        self._preflight_runner = preflight_runner

    def approve(
        self,
        workflow: Any,
    ) -> Any:
        if not isinstance(
            workflow,
            WorkflowResult,
        ):
            raise TypeError(
                "Dashboard approval requires "
                "a WorkflowResult"
            )

        if not workflow.ready_for_approval:
            raise ValueError(
                "Trade workflow is not ready "
                "for approval"
            )

        if not EXECUTION_ENABLED:
            raise RuntimeError(
                "Paper execution is disabled"
            )

        self._validate_freshness(
            workflow
        )

        allowed, reason = (
            self._portfolio_manager
            .can_open_new_trade()
        )

        if not allowed:
            raise RuntimeError(
                "Trade blocked by portfolio limits: "
                f"{reason}"
            )

        fresh_preflight = (
            self._preflight_runner(
                workflow.plan
            )
        )

        if not fresh_preflight.approved:
            reasons = "; ".join(
                fresh_preflight.reasons
            )

            if not reasons:
                reasons = (
                    "Broker preflight rejected "
                    "the trade."
                )

            raise RuntimeError(
                "Trade blocked by fresh broker "
                f"preflight: {reasons}"
            )

        trade_id = str(
            workflow.trade_id or ""
        ).strip()

        if not trade_id:
            trade_id = create_trade_id()

        executable_workflow = replace(
            workflow,
            trade_id=trade_id,
            preflight=fresh_preflight,
        )

        return self._trade_executor.execute(
            executable_workflow
        )

    @staticmethod
    def _validate_freshness(
        workflow: WorkflowResult,
    ) -> None:
        created_at = workflow.created_at

        if not isinstance(
            created_at,
            datetime,
        ):
            raise RuntimeError(
                "Trade workflow timestamp is invalid"
            )

        if (
            created_at.tzinfo is None
            or created_at.utcoffset() is None
        ):
            raise RuntimeError(
                "Trade workflow timestamp is invalid"
            )

        now = datetime.now(
            timezone.utc
        )

        created_at_utc = (
            created_at.astimezone(
                timezone.utc
            )
        )

        age_seconds = (
            now - created_at_utc
        ).total_seconds()

        if age_seconds < 0:
            raise RuntimeError(
                "Trade workflow timestamp is invalid"
            )

        max_age_seconds = (
            MAX_APPROVAL_AGE_MINUTES
            * 60
        )

        if age_seconds > max_age_seconds:
            raise RuntimeError(
                "Trade candidate has expired. "
                "Refresh the dashboard and review "
                "the latest candidate."
            )