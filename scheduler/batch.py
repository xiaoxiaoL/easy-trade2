import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from data.daily import fetch_snapshot
from rules.engine import evaluate
from execution.orders import execute
from storage.log import init_db, log_signal


def run():
    init_db()

    for ticker in config.TICKERS:
        print(f"\n{'=' * 40}")
        print(f"Ticker: {ticker}")

        snapshot = fetch_snapshot(ticker)
        signal, reason = evaluate(snapshot)
        action = execute(snapshot, signal)
        log_signal(snapshot, signal, reason)

        print(f"Date:   {snapshot.date}")
        print(f"Price:  ${snapshot.price:.2f}")
        print(f"MA{config.MA_FAST}:    {snapshot.ma_fast:.2f}")
        print(f"MA{config.MA_SLOW}:   {snapshot.ma_slow:.2f}")
        print(f"RSI:    {snapshot.rsi:.1f}")
        print(f"Signal: {signal.value}")
        print(f"Reason: {reason}")
        print(f"Action: {action}")


if __name__ == "__main__":
    run()
