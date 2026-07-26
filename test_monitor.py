from broker.alpaca_client import create_trading_client
from broker.position_monitor import PositionMonitor


def main() -> None:
    client = create_trading_client()
    monitor = PositionMonitor(client)

    account = monitor.get_account()

    print("=" * 60)
    print("ACCOUNT")
    print("=" * 60)
    print(f"Status: {account.status}")
    print(f"Equity: ${account.equity:,.2f}")
    print(f"Cash: ${account.cash:,.2f}")
    print(f"Buying Power: ${account.buying_power:,.2f}")
    print(f"Trading Blocked: {account.trading_blocked}")
    print(f"Account Blocked: {account.account_blocked}")
    print(f"Shorting Enabled: {account.shorting_enabled}")

    print()
    print("=" * 60)
    print("OPEN POSITIONS")
    print("=" * 60)

    positions = monitor.get_open_positions()

    if not positions:
        print("No open positions.")
    else:
        for position in positions:
            current_price = (
                "N/A"
                if position.current_price is None
                else f"${position.current_price:,.2f}"
            )

            market_value = (
                "N/A"
                if position.market_value is None
                else f"${position.market_value:,.2f}"
            )

            unrealized_pl = (
                "N/A"
                if position.unrealized_profit_loss is None
                else f"${position.unrealized_profit_loss:,.2f}"
            )

            print(
                f"{position.symbol} | "
                f"Side: {position.side} | "
                f"Qty: {position.quantity} | "
                f"Entry: ${position.average_entry_price:,.2f} | "
                f"Current: {current_price} | "
                f"Market Value: {market_value} | "
                f"Unrealized P/L: {unrealized_pl}"
            )

    print()
    print("=" * 60)
    print("OPEN ORDERS")
    print("=" * 60)

    open_orders = monitor.get_open_orders()

    if not open_orders:
        print("No open orders.")
    else:
        for order in open_orders:
            fill_price = (
                "N/A"
                if order.filled_average_price is None
                else f"${order.filled_average_price:,.2f}"
            )

            print(
                f"{order.symbol} | "
                f"Side: {order.side} | "
                f"Status: {order.status} | "
                f"Qty: {order.quantity} | "
                f"Filled: {order.filled_quantity} | "
                f"Fill Price: {fill_price} | "
                f"Class: {order.order_class} | "
                f"Order ID: {order.order_id}"
            )

    print()
    print("=" * 60)
    print("RECENT ORDERS")
    print("=" * 60)

    recent_orders = monitor.get_recent_orders(limit=10)

    if not recent_orders:
        print("No recent orders.")
    else:
        for order in recent_orders:
            fill_price = (
                "N/A"
                if order.filled_average_price is None
                else f"${order.filled_average_price:,.2f}"
            )

            print(
                f"{order.symbol} | "
                f"Side: {order.side} | "
                f"Status: {order.status} | "
                f"Qty: {order.quantity} | "
                f"Filled: {order.filled_quantity} | "
                f"Fill Price: {fill_price} | "
                f"Class: {order.order_class} | "
                f"Order ID: {order.order_id}"
            )


if __name__ == "__main__":
    main()