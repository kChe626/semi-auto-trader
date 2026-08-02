from collections.abc import Callable

from models.preflight_result import PreflightResult
from models.trade_plan import TradePlan
from models.trade_signal import TradeSignal
from models.workflow_result import WorkflowResult
from risk.position_limits import cap_position_size
from risk.signal_to_plan import create_trade_plan_from_signal


PlanBuilder = Callable[..., TradePlan]
RiskLimiter = Callable[..., TradePlan]
PreflightRunner = Callable[[TradePlan], PreflightResult]


def apply_position_limit(
    plan: TradePlan,
    *,
    account_equity: float,
    max_position_percent: float,
) -> TradePlan:
    """
    Apply the portfolio position-size cap to a trade plan.
    """
    quantity = cap_position_size(
        quantity=plan.quantity,
        entry_price=plan.entry_price,
        account_equity=account_equity,
        max_position_percent=max_position_percent,
    )

    plan.quantity = quantity
    plan.total_risk = quantity * plan.risk_per_share

    return plan


class TradeWorkflow:
    """
    Coordinate trade-plan construction, position limiting,
    and broker preflight validation.

    This workflow prepares a trade for manual approval.
    It does not submit an order.
    """

    def __init__(
        self,
        *,
        account_equity: float,
        risk_percent: float,
        max_position_percent: float,
        stop_loss_percent: float | None = None,
        reward_risk_ratio: float = 2.0,
        atr_multiplier: float | None = None,
        plan_builder: PlanBuilder = create_trade_plan_from_signal,
        risk_limiter: RiskLimiter = apply_position_limit,
        preflight_runner: PreflightRunner,
    ) -> None:
        self._account_equity = account_equity
        self._risk_percent = risk_percent
        self._max_position_percent = max_position_percent
        self._stop_loss_percent = stop_loss_percent
        self._reward_risk_ratio = reward_risk_ratio
        self._atr_multiplier = atr_multiplier
        self._plan_builder = plan_builder
        self._risk_limiter = risk_limiter
        self._preflight_runner = preflight_runner

    def create_plan(
        self,
        signal: TradeSignal,
    ) -> TradePlan:
        plan = self._plan_builder(
            signal=signal,
            account_equity=self._account_equity,
            risk_percent=self._risk_percent,
            stop_loss_percent=self._stop_loss_percent,
            reward_risk_ratio=self._reward_risk_ratio,
            atr_multiplier=self._atr_multiplier,
        )

        return self._risk_limiter(
            plan,
            account_equity=self._account_equity,
            max_position_percent=self._max_position_percent,
        )

    def prepare_trade(
        self,
        signal: TradeSignal,
    ) -> WorkflowResult:
        plan = self._plan_builder(
            signal=signal,
            account_equity=self._account_equity,
            risk_percent=self._risk_percent,
            stop_loss_percent=self._stop_loss_percent,
            reward_risk_ratio=self._reward_risk_ratio,
            atr_multiplier=self._atr_multiplier,
        )

        limited_plan = self._risk_limiter(
            plan,
            account_equity=self._account_equity,
            max_position_percent=self._max_position_percent,
        )

        preflight = self._preflight_runner(
            limited_plan
        )

        return WorkflowResult(
            ready_for_approval=preflight.approved,
            plan=limited_plan,
            preflight=preflight,
        )