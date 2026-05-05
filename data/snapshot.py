from dataclasses import dataclass
from datetime import date


@dataclass
class MarketSnapshot:
    ticker: str
    date: date
    price: float
    rsi: float
    pe_ratio: float = 0.0    # trailing P/E (0 = not available)
    pb_ratio: float = 0.0    # price-to-book (0 = not available)
    week52_low: float = 0.0  # 52-week low price
    ma200: float = 0.0       # 200-day moving average (0 = not available)
    pfcf_ratio: float = 0.0  # price-to-free-cash-flow (0 = not available)
    debt_equity: float = 0.0 # debt-to-equity ratio (0 = not available)
    roe: float = 0.0          # return on equity as decimal (0 = not available)
