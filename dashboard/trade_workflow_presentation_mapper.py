from __future__ import annotations

from config.trading_config import (
    MINIMUM_TRADE_SCORE,
)
from dashboard.trade_workflow_presentation_models import (
    TradeWorkflowViewModel,
)
from models.workflow_result import WorkflowResult


class TradeWorkflowPresentationMapper:
    """
    Convert a workflow result into display-ready
    dashboard values.
    """

    def map(
        self,
        result: WorkflowResult | None,
    ) -> TradeWorkflowViewModel:
        if result is None:
            return TradeWorkflowViewModel(
                symbol="—",
                side="—",
                score="—",
                minimum_score=(
                    f"{MINIMUM_TRADE_SCORE:.2f}"
                ),
                entry_price="—",
                stop_price="—",
                target_price="—",
                quantity="—",
                total_risk="—",
                risk_reward_ratio="—",
                status="NO ELIGIBLE TRADE",
                rejection_reasons=(
                    "No eligible trade candidate "
                    "is currently available.",
                ),
            )

        plan = result.plan

        status = (
            "READY FOR APPROVAL"
            if result.ready_for_approval
            else "REJECTED"
        )

        score = (
            f"{result.score:.2f}"
            if result.score is not None
            else "—"
        )

        return TradeWorkflowViewModel(
            symbol=plan.symbol,
            side=plan.signal_type,
            score=score,
            minimum_score=(
                f"{MINIMUM_TRADE_SCORE:.2f}"
            ),
            entry_price=(
                f"${plan.entry_price:,.2f}"
            ),
            stop_price=(
                f"${plan.stop_price:,.2f}"
            ),
            target_price=(
                f"${plan.target_price:,.2f}"
            ),
            quantity=f"{plan.quantity:,}",
            total_risk=(
                f"${plan.total_risk:,.2f}"
            ),
            risk_reward_ratio=(
                f"{plan.risk_reward_ratio:.2f}"
            ),
            status=status,
            rejection_reasons=tuple(
                result.preflight.reasons
            ),
        )