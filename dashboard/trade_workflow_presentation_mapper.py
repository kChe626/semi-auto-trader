from __future__ import annotations

from config.trading_config import (
    ALLOW_LONG_TRADES,
    ALLOW_SHORT_TRADES,
    MINIMUM_TRADE_SCORE,
)
from dashboard.trade_workflow_presentation_models import (
    TradeWorkflowViewModel,
)
from models.trade_signal import TradeSignal
from models.workflow_result import WorkflowResult


class TradeWorkflowPresentationMapper:
    """
    Convert trade-workflow state into display-ready
    dashboard values.
    """

    def map(
        self,
        result: WorkflowResult | None,
        *,
        scanner_signals: tuple[TradeSignal, ...] = (),
    ) -> TradeWorkflowViewModel:
        if result is None:
            return self._map_no_eligible_trade(
                scanner_signals
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

    def _map_no_eligible_trade(
        self,
        scanner_signals: tuple[TradeSignal, ...],
    ) -> TradeWorkflowViewModel:
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
                self._build_no_trade_reasons(
                    scanner_signals
                )
            ),
        )

    @staticmethod
    def _build_no_trade_reasons(
        scanner_signals: tuple[TradeSignal, ...],
    ) -> tuple[str, ...]:
        if not scanner_signals:
            return (
                "No trade signals were found "
                "by the scanner.",
            )

        reasons: list[str] = []

        for signal in scanner_signals:
            signal_type = str(
                signal.signal_type
            ).strip().upper()

            if (
                signal_type == "SELL"
                and not ALLOW_SHORT_TRADES
            ):
                reasons.append(
                    f"{signal.symbol}: SELL signal "
                    "was excluded because short "
                    "trades are disabled."
                )
                continue

            if (
                signal_type == "BUY"
                and not ALLOW_LONG_TRADES
            ):
                reasons.append(
                    f"{signal.symbol}: BUY signal "
                    "was excluded because long "
                    "trades are disabled."
                )
                continue

        if reasons:
            return tuple(reasons)

        return (
            "Scanner signals were found, but no "
            "candidate remained after direction, "
            "risk, preflight, and minimum-score "
            "filters.",
        )