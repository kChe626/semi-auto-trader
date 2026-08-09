from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from models.preflight_result import PreflightResult
from models.trade_plan import TradePlan


@dataclass(frozen=True)
class WorkflowResult:
    ready_for_approval: bool
    plan: TradePlan
    preflight: PreflightResult
    trade_id: str | None = None
    score: float | None = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )