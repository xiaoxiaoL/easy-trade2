import yfinance as yf
import pandas as pd
from datetime import date

import config
from data.snapshot import MarketSnapshot


def fetch_snapshot(ticker: str) -> MarketSnapshot:
    df = yf.download(ticker, period="1y", interval="1d", progress=False, auto_adjust=True)
    close = df["Close"].squeeze()
    rsi = _rsi(close, config.RSI_PERIOD)
    ma200 = float(close.rolling(200).mean().iloc[-1])

    info = yf.Ticker(ticker).info
    pe_ratio = float(info.get("trailingPE") or 0.0)
    pb_ratio = float(info.get("priceToBook") or 0.0)
    week52_low = float(info.get("fiftyTwoWeekLow") or 0.0)
    pfcf_ratio = float(info.get("priceToFreeCashFlow") or 0.0)
    # yfinance returns debtToEquity as a percentage (e.g. 50 = 0.5 ratio)
    debt_equity = float(info.get("debtToEquity") or 0.0) / 100
    # returnOnEquity is a decimal (e.g. 0.15 = 15%)
    roe = float(info.get("returnOnEquity") or 0.0)

    return MarketSnapshot(
        ticker=ticker,
        date=date.today(),
        price=float(close.iloc[-1]),
        rsi=float(rsi.iloc[-1]),
        pe_ratio=pe_ratio,
        pb_ratio=pb_ratio,
        week52_low=week52_low,
        ma200=ma200,
        pfcf_ratio=pfcf_ratio,
        debt_equity=debt_equity,
        roe=roe,
    )


# Keep alias so existing callers still work
fetch_snapshot_with_fundamentals = fetch_snapshot


def _rsi(close: pd.Series, period: int) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))
