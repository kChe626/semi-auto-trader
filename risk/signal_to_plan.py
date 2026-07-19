from models.trade_plan import TradePlan
from models.trade_signal import TradeSignal
from risk.price_levels import calculate_price_levels
from risk.trade_plan_builder import build_trade_plan


def create_trade_plan_from_signal(
    signal: TradeSignal,
    account_equity: float,
    risk_percent: float = 0.01,
    stop_loss_percent: float = 0.02,
    reward_risk_ratio: float = 2.0,
) -> TradePlan:
    """
    Convert a TradeSignal into a complete TradePlan.
    """
    stop_price, target_price = calculate_price_levels(
        signal_type=signal.signal_type,
        entry_price=signal.price,
        stop_loss_percent=stop_loss_percent,
        reward_risk_ratio=reward_risk_ratio,
    )

    return build_trade_plan(
        symbol=signal.symbol,
        signal_type=signal.signal_type,
        account_equity=account_equity,
        risk_percent=risk_percent,
        entry_price=signal.price,
        stop_price=stop_price,
        target_price=target_price,
    )