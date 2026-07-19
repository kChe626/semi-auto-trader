import os

from alpaca.trading.client import TradingClient
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient


load_dotenv()

def create_market_data_client() -> StockHistoricalDataClient:
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")

    if not api_key or not secret_key:
        raise ValueError(
            "Missing ALPACA_API_KEY or ALPACA_SECRET_KEY in the .env file."
        )

    return StockHistoricalDataClient(
        api_key,
        secret_key,
    )

def create_trading_client() -> TradingClient:
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")

    if not api_key or not secret_key:
        raise ValueError(
            "Missing ALPACA_API_KEY or ALPACA_SECRET_KEY in the .env file."
        )

    return TradingClient(
        api_key,
        secret_key,
        paper=True,
    )


def display_account_summary() -> None:
    client = create_trading_client()
    account = client.get_account()

    print("=" * 40)
    print("Connected to Alpaca Paper Trading")
    print("=" * 40)
    print(f"Account Status : {account.status}")
    print(f"Cash           : ${account.cash}")
    print(f"Buying Power   : ${account.buying_power}")
    print(f"Equity         : ${account.equity}")


if __name__ == "__main__":
    display_account_summary()