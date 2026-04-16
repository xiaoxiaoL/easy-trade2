from enum import Enum
from data.snapshot import MarketSnapshot


class Signal(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


def evaluate(snapshot: MarketSnapshot) -> tuple[Signal, str]:
    from rules.basic import ma_crossover_rsi
    return ma_crossover_rsi(snapshot)
