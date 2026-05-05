import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from data.daily import fetch_snapshot_with_fundamentals
from rules.engine import evaluate, Signal
from execution.orders import execute
from storage.log import init_db, log_signal


def get_buy_price(ticker: str) -> float:
    """Return avg cost basis of open position, or 0 if not held."""
    if not config.ALPACA_API_KEY:
        return 0.0
    try:
        from alpaca.trading.client import TradingClient
        client = TradingClient(config.ALPACA_API_KEY, config.ALPACA_SECRET_KEY, paper=True)
        position = client.get_open_position(ticker)
        return float(position.avg_entry_price)
    except Exception:
        return 0.0


def run():
    init_db()
    print(f"Scanning {len(config.TICKERS)} stocks — value filter: P/E<{config.PE_MAX}, RSI buy<{config.RSI_OVERSOLD}, sell>{config.RSI_OVERBOUGHT}\n")

    buy_count = sell_count = error_count = 0

    for ticker in config.TICKERS:
        try:
            snapshot = fetch_snapshot_with_fundamentals(ticker)
        except Exception as e:
            print(f"  {ticker}: fetch error — {e}")
            error_count += 1
            continue

        buy_price = get_buy_price(snapshot.ticker)
        signal, reason = evaluate(snapshot, buy_price)
        action = execute(snapshot, signal)
        log_signal(snapshot, signal, reason)

        if signal == Signal.BUY:
            buy_count += 1
        elif signal == Signal.SELL:
            sell_count += 1

        if signal != Signal.HOLD:
            print(f"{'=' * 45}")
            print(f"Ticker: {ticker}")
            print(f"Price:  ${snapshot.price:.2f}  |  P/E: {snapshot.pe_ratio:.1f}")
            print(f"RSI:    {snapshot.rsi:.1f}")
            print(f"Signal: {signal.value}")
            print(f"Reason: {reason}")
            print(f"Action: {action}\n")

    print(f"{'=' * 45}")
    print(f"Done — BUY: {buy_count}  SELL: {sell_count}  Errors: {error_count}")


if __name__ == "__main__":
    run()
