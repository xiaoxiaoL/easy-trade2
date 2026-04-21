"""
Compare MA strategies on SPY.
Usage: python compare.py
"""

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from data.snapshot import MarketSnapshot
from rules.engine import Signal


def load_history(ticker: str, period: str, ma_fast: int, ma_slow: int) -> pd.DataFrame:
    df = yf.download(ticker, period=period, interval="1d",
                     progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    close = df["Close"].squeeze()
    df["ma_fast"] = close.rolling(ma_fast).mean()
    df["ma_slow"] = close.rolling(ma_slow).mean()
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    df["rsi"] = 100 - (100 / (1 + gain / loss))
    return df.dropna()


def simulate(df, ma_fast, ma_slow, rsi_threshold=50,
             starting_cash=100_000.0, position_pct=0.50):
    cash = starting_cash
    shares = 0
    trades = []

    for i in range(1, len(df)):
        row = df.iloc[i]
        prev = df.iloc[i - 1]
        price = float(row["Close"])

        snapshot = MarketSnapshot(
            ticker="SPY", date=df.index[i].date(), price=price,
            ma_fast=float(row["ma_fast"]), ma_slow=float(row["ma_slow"]),
            prev_ma_fast=float(prev["ma_fast"]), prev_ma_slow=float(prev["ma_slow"]),
            rsi=float(row["rsi"]),
        )

        golden = snapshot.prev_ma_fast < snapshot.prev_ma_slow and snapshot.ma_fast > snapshot.ma_slow
        death  = snapshot.prev_ma_fast > snapshot.prev_ma_slow and snapshot.ma_fast < snapshot.ma_slow

        if golden and snapshot.rsi > rsi_threshold and shares == 0:
            shares = int((cash * position_pct) / price)
            cash -= shares * price
            trades.append({"date": df.index[i], "action": "BUY", "price": price})

        elif death and snapshot.rsi < rsi_threshold and shares > 0:
            cash += shares * price
            trades.append({"date": df.index[i], "action": "SELL", "price": price, "shares": shares})
            shares = 0

    last_price = float(df.iloc[-1]["Close"])
    final_value = cash + shares * last_price
    ret = (final_value - starting_cash) / starting_cash * 100

    completed = list(zip(
        [t for t in trades if t["action"] == "BUY"],
        [t for t in trades if t["action"] == "SELL"],
    ))
    wins = sum(1 for b, s in completed if s["price"] > b["price"])
    win_rate = wins / len(completed) * 100 if completed else 0

    return trades, final_value, ret, len(trades), len(completed), win_rate


def compare(ticker="SPY", period="1y"):
    configs = [
        {"ma_fast": 3, "ma_slow": 10, "label": "MA3/10 (active)"},
        {"ma_fast": 5, "ma_slow": 20, "label": "MA5/20 (swing)"},
    ]

    starting_cash = 100_000.0

    # Buy & hold benchmark
    raw = yf.download(ticker, period=period, interval="1d",
                      progress=False, auto_adjust=True)
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)
    close = raw["Close"].squeeze()
    first_price = float(close.iloc[0])
    last_price  = float(close.iloc[-1])
    bh_shares = int((starting_cash * 0.50) / first_price)
    bh_value = (starting_cash - bh_shares * first_price) + bh_shares * last_price
    bh_return = (bh_value - starting_cash) / starting_cash * 100

    print(f"\nComparison: {ticker} | Period: {period}\n")
    print(f"{'Strategy':<20} {'Return':>8} {'Trades':>8} {'Completed':>10} {'Win Rate':>10}")
    print("-" * 60)

    results = []
    for cfg in configs:
        df = load_history(ticker, period, cfg["ma_fast"], cfg["ma_slow"])
        trades, final_value, ret, total, completed, win_rate = simulate(df, cfg["ma_fast"], cfg["ma_slow"])
        print(f"{cfg['label']:<20} {ret:>+7.1f}% {total:>8d} {completed:>10d} {win_rate:>9.0f}%")
        results.append((cfg, df, trades, ret))

    print(f"{'Buy & Hold':<20} {bh_return:>+7.1f}%")
    print("-" * 60)

    # Chart
    fig, axes = plt.subplots(len(configs), 1, figsize=(14, 5 * len(configs)), sharex=False)
    fig.suptitle(f"{ticker} Strategy Comparison — {period}", fontsize=13, fontweight="bold")

    for ax, (cfg, df, trades, ret) in zip(axes, results):
        dates = df.index
        ax.plot(dates, df["Close"], color="#333", linewidth=1.2, label="SPY")
        ax.plot(dates, df["ma_fast"], color="#2196F3", linewidth=1, linestyle="--",
                label=f"MA{cfg['ma_fast']}")
        ax.plot(dates, df["ma_slow"], color="#FF9800", linewidth=1.4,
                label=f"MA{cfg['ma_slow']}")

        buy_dates  = [t["date"] for t in trades if t["action"] == "BUY"]
        buy_prices = [t["price"] for t in trades if t["action"] == "BUY"]
        sell_dates  = [t["date"] for t in trades if t["action"] == "SELL"]
        sell_prices = [t["price"] for t in trades if t["action"] == "SELL"]

        ax.scatter(buy_dates,  buy_prices,  marker="^", color="#4CAF50", s=100, zorder=5, label="BUY")
        ax.scatter(sell_dates, sell_prices, marker="v", color="#F44336", s=100, zorder=5, label="SELL")

        ax.set_title(f"{cfg['label']}  |  Return: {ret:+.1f}%  |  "
                     f"Trades: {len(trades)}  |  B&H: {bh_return:+.1f}%")
        ax.set_ylabel("Price ($)")
        ax.legend(loc="upper left", fontsize=9)
        ax.grid(alpha=0.3)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=30)

    plt.tight_layout()
    plt.savefig("compare_chart.png", dpi=150, bbox_inches="tight")
    print("\nChart saved → compare_chart.png")


if __name__ == "__main__":
    compare(ticker="SPY", period="1y")
