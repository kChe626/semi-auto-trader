from broker.alpaca_client import create_trading_client
from config.trading_config import (
    MAX_POSITION_PERCENT,
    REWARD_RISK_RATIO,
    RISK_PERCENT,
    STOP_LOSS_PERCENT,
)
from config.watchlist import WATCHLIST
from risk.plan_formatter import format_trade_plan
from risk.risk_manager import RiskManager
from risk.signal_to_plan import create_trade_plan_from_signal
from scanner.scanner import scan_market


def main() -> None:
    trading_client = create_trading_client()

    account = trading_client.get_account()
    account_equity = float(account.equity)

    risk_manager = RiskManager(
        account_equity=account_equity,
        max_position_percent=MAX_POSITION_PERCENT,
    )

    print(f"Account Equity: ${account_equity:,.2f}")
    print(f"Scanning {len(WATCHLIST)} symbols...")

    signals = scan_market()

    if not signals:
        print("\nNo valid trade signals found.")
        return

    for signal in signals:
        plan = create_trade_plan_from_signal(
            signal=signal,
            account_equity=account_equity,
            risk_percent=RISK_PERCENT,
            stop_loss_percent=STOP_LOSS_PERCENT,
            reward_risk_ratio=REWARD_RISK_RATIO,
        )

        plan = risk_manager.apply_position_limit(plan)

        if plan.quantity <= 0:
            print(
                f"\nSkipping {plan.symbol}: "
                "quantity is zero after risk limits."
            )
            continue

        print(format_trade_plan(plan))


if __name__ == "__main__":
    main()