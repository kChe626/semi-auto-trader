from __future__ import annotations

from collections.abc import Callable
from typing import Any


class TradeExecutionService:
    """
    Coordinates human approval and trade execution.

    Approval happens before execution.
    This service does not create plans or manage risk.
    """

    def __init__(
        self,
        *,
        trade_approval: Callable[[Any], bool],
        trade_executor: Callable[[Any], Any],
    ) -> None:
        self._trade_approval = trade_approval
        self._trade_executor = trade_executor

    def execute(
        self,
        workflow: Any,
    ) -> Any | None:
        plan = workflow.plan

        approved = self._trade_approval(
            plan
        )

        if not approved:
            return None

        return self._trade_executor(
            workflow
        )