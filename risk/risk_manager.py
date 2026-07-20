from models.trade_plan import TradePlan
from risk.position_limits import cap_position_size


class RiskManager:
    """
    Applies portfolio-level risk rules to a TradePlan.
    """

    def __init__(
        self,
        account_equity: float,
        max_position_percent: float,
    ) -> None:
        self.account_equity = account_equity
        self.max_position_percent = max_position_percent

    def apply_position_limit(
        self,
        plan: TradePlan,
    ) -> TradePlan:
        """
        Reduce share quantity if position value exceeds the maximum allowed.
        """
        quantity = cap_position_size(
            quantity=plan.quantity,
            entry_price=plan.entry_price,
            account_equity=self.account_equity,
            max_position_percent=self.max_position_percent,
        )

        plan.quantity = quantity
        plan.total_risk = quantity * plan.risk_per_share

        return plan