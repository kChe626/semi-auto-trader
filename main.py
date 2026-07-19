from broker.alpaca_client import create_trading_client
from config.watchlist import WATCHLIST
from risk.plan_formatter import format_trade_plan
from risk.signal_to_plan import create_trade_plan_from_signal
from scanner.scanner import scan_market


RISK_PERCENT = 0.01
STOP_LOSS_PERCENT = 0.02
REWARD_RISK_RATIO = 2.0


def main() -> None:
    trading_client = create_trading_client()
    account = trading_client.get_account()
    account_equity = float(account.equity)

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

        print(format_trade_plan(plan))


if __name__ == "__main__":
    main()