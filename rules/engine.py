from enum import Enum
from data.snapshot import MarketSnapshot


class Signal(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


def evaluate(snapshot: MarketSnapshot, buy_price: float = 0.0) -> tuple[Signal, str]:
    from rules.basic import undervalued_rsi
    return undervalued_rsi(snapshot, buy_price)
