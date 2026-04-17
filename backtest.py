"""
Backtest the 5/20 MA crossover + RSI strategy on SPY historical data.
Usage: python backtest.py
"""

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import config
from data.snapshot import MarketSnapshot
from rules.engine import evaluate, Signal


def load_history(ticker: str, period: str = "2y") -> pd.DataFrame:
    df = yf.download(ticker, period=period, interval="1d",
                     progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    close = df["Close"].squeeze()

    df["ma_fast"] = close.rolling(config.MA_FAST).mean()
    df["ma_slow"] = close.rolling(config.MA_SLOW).mean()

    delta = close.diff()
    gain = delta.clip(lower=0).rolling(config.RSI_PERIOD).mean()
    loss = (-delta.clip(upper=0)).rolling(config.RSI_PERIOD).mean()
    df["rsi"] = 100 - (100 / (1 + gain / loss))

    return df.dropna()


def run_backtest(ticker: str = "SPY", period: str = "2y",
                 starting_cash: float = 100_000.0):
    print(f"\nBacktest: {ticker} | Period: {period} | "
          f"Strategy: MA{config.MA_FAST}/{config.MA_SLOW} crossover + RSI\n")

    df = load_history(ticker, period)

    cash = starting_cash
    shares = 0
    trades = []

    for i in range(1, len(df)):
        row = df.iloc[i]
        prev = df.iloc[i - 1]
        price = float(row["Close"])
        today = df.index[i].date()

        snapshot = MarketSnapshot(
            ticker=ticker,
            date=today,
            price=price,
            ma_fast=float(row["ma_fast"]),
            ma_slow=float(row["ma_slow"]),
            prev_ma_fast=float(prev["ma_fast"]),
            prev_ma_slow=float(prev["ma_slow"]),
            rsi=float(row["rsi"]),
        )

        signal, reason = evaluate(snapshot)

        if signal == Signal.BUY and shares == 0:
            shares = int((cash * config.MAX_POSITION_PCT) / price)
            cash -= shares * price
            trades.append({"date": today, "action": "BUY",
                            "price": price, "shares": shares, "cash": cash})

        elif signal == Signal.SELL and shares > 0:
            cash += shares * price
            trades.append({"date": today, "action": "SELL",
                            "price": price, "shares": shares, "cash": cash})
            shares = 0

    last_price = float(df.iloc[-1]["Close"])
    portfolio_value = cash + shares * last_price
    first_price = float(df.iloc[0]["Close"])
    bh_shares = int((starting_cash * config.MAX_POSITION_PCT) / first_price)
    bh_value = (starting_cash - bh_shares * first_price) + bh_shares * last_price

    _print_results(trades, starting_cash, portfolio_value, bh_value, shares, last_price)
    _plot(df, trades, ticker, starting_cash, portfolio_value, bh_value)


def _print_results(trades, starting_cash, portfolio_value, bh_value, open_shares, last_price):
    buy_trades = [t for t in trades if t["action"] == "BUY"]
    sell_trades = [t for t in trades if t["action"] == "SELL"]

    pnl_list = []
    for buy, sell in zip(buy_trades, sell_trades):
        pnl = (sell["price"] - buy["price"]) * sell["shares"]
        pnl_pct = (sell["price"] - buy["price"]) / buy["price"] * 100
        pnl_list.append((buy["date"], sell["date"], buy["price"],
                         sell["price"], sell["shares"], pnl, pnl_pct))

    wins = [p for p in pnl_list if p[5] > 0]
    losses = [p for p in pnl_list if p[5] <= 0]
    strategy_return = (portfolio_value - starting_cash) / starting_cash * 100
    bh_return = (bh_value - starting_cash) / starting_cash * 100

    print(f"{'=' * 55}")
    print(f"  TRADE LOG")
    print(f"{'=' * 55}")
    for t in trades:
        print(f"  {t['date']}  {t['action']:4s}  "
              f"{t['shares']:4d} shares @ ${t['price']:7.2f}")
    if open_shares > 0:
        print(f"\n  * Still holding {open_shares} shares "
              f"(valued at ${open_shares * last_price:,.0f})")

    print(f"\n{'=' * 55}")
    print(f"  COMPLETED TRADES P&L")
    print(f"{'=' * 55}")
    if pnl_list:
        for buy_d, sell_d, bp, sp, _, pnl, pct in pnl_list:
            flag = "✓" if pnl > 0 else "✗"
            print(f"  {flag} {buy_d} → {sell_d}  "
                  f"${bp:.2f}→${sp:.2f}  P&L: ${pnl:+,.0f} ({pct:+.1f}%)")
    else:
        print("  No completed round-trip trades yet.")

    print(f"\n{'=' * 55}")
    print(f"  SUMMARY")
    print(f"{'=' * 55}")
    print(f"  Starting cash:       ${starting_cash:>10,.0f}")
    print(f"  Final value:         ${portfolio_value:>10,.0f}")
    print(f"  Strategy return:     {strategy_return:>+9.1f}%")
    print(f"  Buy & hold return:   {bh_return:>+9.1f}%")
    print(f"  Total signals:       {len(trades):>10d}")
    print(f"  Completed trades:    {len(pnl_list):>10d}")
    if pnl_list:
        win_rate = len(wins) / len(pnl_list) * 100
        avg_win = sum(p[5] for p in wins) / len(wins) if wins else 0
        avg_loss = sum(p[5] for p in losses) / len(losses) if losses else 0
        print(f"  Win rate:            {win_rate:>9.0f}%")
        print(f"  Avg win:             ${avg_win:>+9,.0f}")
        print(f"  Avg loss:            ${avg_loss:>+9,.0f}")
    print(f"{'=' * 55}\n")


def _plot(df, trades, ticker, starting_cash, portfolio_value, bh_value):
    strategy_return = (portfolio_value - starting_cash) / starting_cash * 100
    bh_return = (bh_value - starting_cash) / starting_cash * 100

    buy_dates  = [t["date"] for t in trades if t["action"] == "BUY"]
    buy_prices = [t["price"] for t in trades if t["action"] == "BUY"]
    sell_dates  = [t["date"] for t in trades if t["action"] == "SELL"]
    sell_prices = [t["price"] for t in trades if t["action"] == "SELL"]

    dates = df.index

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8),
                                    gridspec_kw={"height_ratios": [3, 1]},
                                    sharex=True)
    fig.suptitle(
        f"{ticker} — MA{config.MA_FAST}/{config.MA_SLOW} Crossover + RSI  |  "
        f"Strategy: {strategy_return:+.1f}%  vs  Buy & Hold: {bh_return:+.1f}%",
        fontsize=13, fontweight="bold"
    )

    # --- Price + MAs ---
    ax1.plot(dates, df["Close"], color="#333333", linewidth=1.2, label="SPY Price")
    ax1.plot(dates, df["ma_fast"], color="#2196F3", linewidth=1.2,
             linestyle="--", label=f"MA{config.MA_FAST}")
    ax1.plot(dates, df["ma_slow"], color="#FF9800", linewidth=1.5,
             label=f"MA{config.MA_SLOW}")

    # Shade held periods
    in_trade = False
    trade_start = None
    for t in trades:
        if t["action"] == "BUY":
            in_trade = True
            trade_start = pd.Timestamp(t["date"])
        elif t["action"] == "SELL" and in_trade:
            ax1.axvspan(trade_start, pd.Timestamp(t["date"]),
                        alpha=0.08, color="green")
            in_trade = False
    if in_trade:
        ax1.axvspan(trade_start, dates[-1], alpha=0.08, color="green")

    # BUY / SELL markers
    ax1.scatter(pd.to_datetime(buy_dates), buy_prices,
                marker="^", color="#4CAF50", s=120, zorder=5, label="BUY")
    ax1.scatter(pd.to_datetime(sell_dates), sell_prices,
                marker="v", color="#F44336", s=120, zorder=5, label="SELL")

    ax1.set_ylabel("Price ($)")
    ax1.legend(loc="upper left", fontsize=9)
    ax1.grid(alpha=0.3)

    # --- RSI ---
    ax2.plot(dates, df["rsi"], color="#9C27B0", linewidth=1.2, label="RSI")
    ax2.axhline(config.RSI_BUY_THRESHOLD, color="#4CAF50",
                linestyle="--", linewidth=0.8, label=f"RSI {config.RSI_BUY_THRESHOLD}")
    ax2.axhline(config.RSI_SELL_THRESHOLD, color="#F44336",
                linestyle="--", linewidth=0.8)
    ax2.axhline(70, color="#F44336", linestyle=":", linewidth=0.6, alpha=0.5)
    ax2.axhline(30, color="#4CAF50", linestyle=":", linewidth=0.6, alpha=0.5)
    ax2.fill_between(dates, df["rsi"], 70,
                     where=(df["rsi"] >= 70), alpha=0.15, color="#F44336")
    ax2.fill_between(dates, df["rsi"], 30,
                     where=(df["rsi"] <= 30), alpha=0.15, color="#4CAF50")
    ax2.set_ylim(0, 100)
    ax2.set_ylabel("RSI")
    ax2.legend(loc="upper left", fontsize=9)
    ax2.grid(alpha=0.3)

    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.xticks(rotation=30)

    plt.tight_layout()
    plt.savefig("backtest_chart.png", dpi=150, bbox_inches="tight")
    print("Chart saved → backtest_chart.png")


if __name__ == "__main__":
    run_backtest(ticker="SPY", period="2y")
