from scanner.scanner import scan_market


def main() -> None:
    buy_signals = scan_market()

    print("\nToday's Buy Signals")
    print("-" * 25)

    if buy_signals:
        for symbol in buy_signals:
            print(symbol)
    else:
        print("No buy signals today.")


if __name__ == "__main__":
    main()