from models.trade_plan import TradePlan
from models.trade_signal import TradeSignal
from risk.atr_price_levels import calculate_atr_price_levels
from risk.position_sizer import calculate_position_size
from risk.price_levels import calculate_price_levels


def create_trade_plan_from_signal(
    signal: TradeSignal,
    account_equity: float,
    risk_percent: float,
    stop_loss_percent: float | None = None,
    reward_risk_ratio: float = 2.0,
    atr_multiplier: float | None = None,
) -> TradePlan:
    """
    Convert a TradeSignal into a fully sized TradePlan.

    Uses ATR-based price levels when atr_multiplier is provided.
    Otherwise, uses the existing percentage-based stop-loss logic.
    """
    if atr_multiplier is not None:
        if signal.atr is None:
            raise ValueError(
                "ATR is required when atr_multiplier is provided"
            )

        stop_price, target_price = calculate_atr_price_levels(
            entry_price=signal.price,
            atr=signal.atr,
            signal_type=signal.signal_type,
            atr_multiplier=atr_multiplier,
            reward_ratio=reward_risk_ratio,
        )
    else:
        if stop_loss_percent is None:
            raise ValueError(
                "stop_loss_percent is required when ATR pricing is not used"
            )

        stop_price, target_price = calculate_price_levels(
            entry_price=signal.price,
            signal_type=signal.signal_type,
            stop_loss_percent=stop_loss_percent,
            reward_risk_ratio=reward_risk_ratio,
        )

    quantity = calculate_position_size(
        account_equity=account_equity,
        risk_percent=risk_percent,
        entry_price=signal.price,
        stop_price=stop_price,
    )

    risk_per_share = abs(signal.price - stop_price)
    reward_per_share = abs(target_price - signal.price)
    total_risk = risk_per_share * quantity

    actual_risk_reward_ratio = (
        reward_per_share / risk_per_share
    )

    return TradePlan(
        symbol=signal.symbol,
        signal_type=signal.signal_type,
        entry_price=signal.price,
        stop_price=stop_price,
        target_price=target_price,
        quantity=quantity,
        risk_per_share=risk_per_share,
        reward_per_share=reward_per_share,
        total_risk=total_risk,
        risk_reward_ratio=actual_risk_reward_ratio,
        rsi=signal.rsi,
        short_sma=signal.short_sma,
        long_sma=signal.long_sma,
    )