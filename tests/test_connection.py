from broker.alpaca_client import create_trading_client


def main() -> None:
    client = create_trading_client()
    account = client.get_account()

    print("Alpaca paper connection successful.")
    print(f"Account status: {account.status}")
    print(f"Equity: ${account.equity}")


if __name__ == "__main__":
    main()