from dataclasses import dataclass
from datetime import date


@dataclass
class MarketSnapshot:
    ticker: str
    date: date
    price: float
    ma_fast: float       # MA5 today
    ma_slow: float       # MA20 today
    prev_ma_fast: float  # MA5 yesterday
    prev_ma_slow: float  # MA20 yesterday
    rsi: float
