import yfinance as yf

from alpaca.data.requests import StockLatestBarRequest

from broker.alpaca_client import create_market_data_client


def get_latest_bar(symbol: str):
    data_client = create_market_data_client()

    request = StockLatestBarRequest(
        symbol_or_symbols=symbol,
    )

    bars = data_client.get_stock_latest_bar(request)
    return bars[symbol]


def get_historical_bars(symbol: str):
    bars = yf.download(
        tickers=symbol,
        period="6mo",
        interval="1d",
        auto_adjust=False,
        progress=False,
    )

    bars.columns = bars.columns.get_level_values(0)

    return bars


def display_latest_bar(symbol: str) -> None:
    bar = get_latest_bar(symbol)

    print("=" * 40)
    print(f"Latest {symbol} Bar")
    print("=" * 40)
    print(f"Time   : {bar.timestamp}")
    print(f"Open   : ${bar.open}")
    print(f"High   : ${bar.high}")
    print(f"Low    : ${bar.low}")
    print(f"Close  : ${bar.close}")
    print(f"Volume : {int(bar.volume):,}")