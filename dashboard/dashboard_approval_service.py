from __future__ import annotations

from dataclasses import replace
from typing import Any, Protocol

from config.trading_config import EXECUTION_ENABLED
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


class DashboardApprovalService:
    """
    Approve and execute dashboard trade workflows.

    Execution remains disabled unless explicitly enabled
    in trading configuration.
    """

    def __init__(
        self,
        *,
        trade_executor: TradeExecutorProtocol,
    ) -> None:
        self._trade_executor = trade_executor

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

        if not workflow.preflight.approved:
            raise ValueError(
                "Trade workflow did not pass "
                "broker preflight"
            )

        if not EXECUTION_ENABLED:
            raise RuntimeError(
                "Paper execution is disabled"
            )

        trade_id = str(
            workflow.trade_id or ""
        ).strip()

        if not trade_id:
            trade_id = create_trade_id()

        executable_workflow = replace(
            workflow,
            trade_id=trade_id,
        )

        return self._trade_executor.execute(
            executable_workflow
        )