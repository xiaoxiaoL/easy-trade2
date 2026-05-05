"""
Backtest value strategy (P/E <= PE_MAX and RSI oversold/overbought)
on Dow 30 stocks over the past year.

Note: uses current P/E as a static filter (historical P/E not available via yfinance).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

import config


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def backtest_ticker(close: pd.Series, pe_ratio: float) -> dict:
    rsi_series = rsi(close, config.RSI_PERIOD)
    pe_qualifies = 0 < pe_ratio <= config.PE_MAX

    cash = 10_000.0
    position = 0
    buy_price = 0.0
    trades = 0
    wins = 0
    blacklisted_until = -1  # index — no re-entry until after this

    for i in range(1, len(close)):
        price = float(close.iloc[i])
        r = float(rsi_series.iloc[i])
        if pd.isna(r):
            continue

        if pe_qualifies and position == 0 and i > blacklisted_until and r <= config.RSI_OVERSOLD:
            shares = cash / price  # fractional
            if shares > 0:
                cash -= shares * price
                position = shares
                buy_price = price
                trades += 1

        elif position > 0:
            loss_pct = (price - buy_price) / buy_price
            if r >= config.RSI_OVERBOUGHT or loss_pct <= -config.STOP_LOSS:
                if price > buy_price:
                    wins += 1
                cash += position * price
                position = 0
                if loss_pct <= -config.STOP_LOSS:
                    blacklisted_until = i + 30  # 30-day cooldown after stop-loss

    # Close any open position
    if position > 0:
        cash += position * float(close.iloc[-1])

    strategy_pct = (cash - 10_000) / 10_000 * 100
    bh_pct = (float(close.iloc[-1]) - float(close.iloc[0])) / float(close.iloc[0]) * 100
    return dict(pe_qualifies=pe_qualifies, strategy_pct=strategy_pct,
                bh_pct=bh_pct, trades=trades, wins=wins)


def main():
    print(f"Backtesting value strategy on S&P 100 (1 year)")
    print(f"Buy: P/E <= {config.PE_MAX} AND RSI <= {config.RSI_OVERSOLD}")
    print(f"Sell: RSI >= {config.RSI_OVERBOUGHT}\n")

    rows = []
    for ticker in config.TICKERS:
        try:
            df = yf.download(ticker, period="1y", interval="1d", progress=False, auto_adjust=True)
            close = df["Close"].squeeze()
            info = yf.Ticker(ticker).info
            pe = float(info.get("trailingPE") or 0.0)
            r = backtest_ticker(close, pe)
            rows.append(dict(ticker=ticker, pe=pe, **r))
        except Exception as e:
            print(f"  {ticker}: error — {e}")

    # Print table
    print(f"{'Ticker':<8} {'P/E':>6} {'Filter':>7} {'Strategy':>10} {'B&H':>8} {'Trades':>7} {'Wins':>5}")
    print("-" * 55)
    for r in sorted(rows, key=lambda x: x["strategy_pct"], reverse=True):
        qualifier = "PASS" if r["pe_qualifies"] else "fail"
        pe_str = f"{r['pe']:.1f}" if r["pe"] > 0 else "N/A"
        win_str = f"{r['wins']}/{r['trades']}" if r["trades"] > 0 else "—"
        print(f"{r['ticker']:<8} {pe_str:>6} {qualifier:>7} {r['strategy_pct']:>+9.1f}% {r['bh_pct']:>+7.1f}% {r['trades']:>7} {win_str:>5}")

    qualifying = [r for r in rows if r["pe_qualifies"]]
    all_rows = rows

    print(f"\n{'='*55}")
    print(f"Stocks passing P/E filter: {len(qualifying)}/{len(rows)}")
    if qualifying:
        avg_s = sum(r["strategy_pct"] for r in qualifying) / len(qualifying)
        avg_b = sum(r["bh_pct"] for r in qualifying) / len(qualifying)
        print(f"Avg strategy (qualifying): {avg_s:+.1f}%")
        print(f"Avg B&H      (qualifying): {avg_b:+.1f}%")
    avg_bh_all = sum(r["bh_pct"] for r in all_rows) / len(all_rows)
    print(f"Avg B&H      (all Dow 30): {avg_bh_all:+.1f}%")

    # Chart: strategy vs B&H for qualifying stocks
    if qualifying:
        tickers = [r["ticker"] for r in qualifying]
        strat = [r["strategy_pct"] for r in qualifying]
        bh = [r["bh_pct"] for r in qualifying]

        x = range(len(tickers))
        fig, ax = plt.subplots(figsize=(max(8, len(tickers)), 5))
        ax.bar([i - 0.2 for i in x], strat, 0.4, label="Strategy", color="steelblue")
        ax.bar([i + 0.2 for i in x], bh, 0.4, label="Buy & Hold", color="orange")
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_xticks(list(x))
        ax.set_xticklabels(tickers, rotation=45)
        ax.set_ylabel("Return (%)")
        ax.set_title(f"Value Strategy vs Buy & Hold (1y) — P/E≤{config.PE_MAX}, RSI buy≤{config.RSI_OVERSOLD}, sell≥{config.RSI_OVERBOUGHT}")
        ax.legend()
        plt.tight_layout()
        plt.savefig("backtest.png")
        print(f"\nChart saved to backtest.png")


if __name__ == "__main__":
    main()
