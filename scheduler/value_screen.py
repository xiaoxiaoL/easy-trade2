import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from data.daily import fetch_snapshot
from rules.value import value_screen
from datetime import date


def run():
    print(f"Value Screen — {date.today()}")
    print(
        f"Filters: P/E<{config.VALUE_PE_MAX}, P/B<{config.VALUE_PB_MAX}, "
        f"P/FCF<{config.VALUE_PFCF_MAX}, D/E<{config.VALUE_DE_MAX}, "
        f"ROE>{config.VALUE_ROE_MIN * 100:.0f}%"
    )
    print(f"Universe: {len(config.TICKERS)} stocks (S&P 100)\n")

    results = []

    for ticker in config.TICKERS:
        try:
            snapshot = fetch_snapshot(ticker)
            score, filters_passed = value_screen(snapshot)
            results.append((ticker, score, snapshot, filters_passed))
            print(f"  {ticker}: {score}/5 filters", flush=True)
        except Exception as e:
            print(f"  {ticker}: error — {e}", flush=True)

    # Sort by score desc, then P/E asc (cheapest first among equal scores)
    results.sort(key=lambda x: (-x[1], x[2].pe_ratio if x[2].pe_ratio > 0 else 999))

    # Candidates: 3 or more filters passed
    candidates = [r for r in results if r[1] >= 3]

    print(f"\n{'=' * 55}")
    print(f"CANDIDATES — passing 3+ of 5 filters ({len(candidates)} found)")
    print(f"{'=' * 55}")

    for ticker, score, snap, filters in candidates[:10]:
        print(f"\n  {ticker}  [{score}/5]  ${snap.price:.2f}")
        for f in filters:
            print(f"    + {f}")

    print(f"\n{'=' * 55}")
    print("TOP 3 PICKS FOR THE YEAR")
    print(f"{'=' * 55}")

    top3 = candidates[:3]
    if top3:
        for rank, (ticker, score, snap, filters) in enumerate(top3, 1):
            print(
                f"  {rank}. {ticker:<6}  {score}/5 filters  "
                f"P/E={snap.pe_ratio:.1f}  P/B={snap.pb_ratio:.2f}  "
                f"ROE={snap.roe * 100:.1f}%  price=${snap.price:.2f}"
            )
    else:
        print("  No stocks passed 3+ filters — market may be expensive right now.")
        print("  Consider lowering thresholds or broadening the ticker universe.")

    print(f"{'=' * 55}")


if __name__ == "__main__":
    run()
