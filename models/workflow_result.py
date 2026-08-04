from __future__ import annotations

from dataclasses import dataclass

from models.preflight_result import PreflightResult
from models.trade_plan import TradePlan


@dataclass(frozen=True)
class WorkflowResult:
    ready_for_approval: bool
    plan: TradePlan
    preflight: PreflightResult
    trade_id: str | None = None