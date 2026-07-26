from dashboard.trade_workflow_presentation_models import (
    TradeWorkflowViewModel,
)
from models.workflow_result import WorkflowResult


class TradeWorkflowPresentationMapper:
    """
    Convert a workflow result into display-ready dashboard values.
    """

    def map(
        self,
        result: WorkflowResult,
    ) -> TradeWorkflowViewModel:
        plan = result.plan

        status = (
            "READY FOR APPROVAL"
            if result.ready_for_approval
            else "REJECTED"
        )

        return TradeWorkflowViewModel(
            symbol=plan.symbol,
            side=plan.signal_type,
            entry_price=f"${plan.entry_price:,.2f}",
            stop_price=f"${plan.stop_price:,.2f}",
            target_price=f"${plan.target_price:,.2f}",
            quantity=f"{plan.quantity:,}",
            total_risk=f"${plan.total_risk:,.2f}",
            risk_reward_ratio=(
                f"{plan.risk_reward_ratio:.2f}"
            ),
            status=status,
            rejection_reasons=tuple(
                result.preflight.reasons
            ),
        )