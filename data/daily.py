import yfinance as yf
import pandas as pd
from datetime import date

import config
from data.snapshot import MarketSnapshot


def fetch_snapshot(ticker: str) -> MarketSnapshot:
    # Fetch enough history for MA20 + RSI14 (60 days is plenty)
    df = yf.download(ticker, period="60d", interval="1d", progress=False, auto_adjust=True)
    close = df["Close"].squeeze()

    ma_fast = close.rolling(config.MA_FAST).mean()
    ma_slow = close.rolling(config.MA_SLOW).mean()
    rsi = _rsi(close, config.RSI_PERIOD)

    return MarketSnapshot(
        ticker=ticker,
        date=date.today(),
        price=float(close.iloc[-1]),
        ma_fast=float(ma_fast.iloc[-1]),
        ma_slow=float(ma_slow.iloc[-1]),
        prev_ma_fast=float(ma_fast.iloc[-2]),
        prev_ma_slow=float(ma_slow.iloc[-2]),
        rsi=float(rsi.iloc[-1]),
    )


def _rsi(close: pd.Series, period: int) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))
