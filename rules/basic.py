import config
from data.snapshot import MarketSnapshot
from rules.engine import Signal


def ma_crossover_rsi(snapshot: MarketSnapshot) -> tuple[Signal, str]:
    golden_cross = (snapshot.prev_ma_fast < snapshot.prev_ma_slow and
                    snapshot.ma_fast > snapshot.ma_slow)

    death_cross = (snapshot.prev_ma_fast > snapshot.prev_ma_slow and
                   snapshot.ma_fast < snapshot.ma_slow)

    if golden_cross and snapshot.rsi > config.RSI_BUY_THRESHOLD:
        return Signal.BUY, (
            f"Golden cross: MA{config.MA_FAST}={snapshot.ma_fast:.2f} crossed above "
            f"MA{config.MA_SLOW}={snapshot.ma_slow:.2f}, RSI={snapshot.rsi:.1f}"
        )

    if death_cross and snapshot.rsi < config.RSI_SELL_THRESHOLD:
        return Signal.SELL, (
            f"Death cross: MA{config.MA_FAST}={snapshot.ma_fast:.2f} crossed below "
            f"MA{config.MA_SLOW}={snapshot.ma_slow:.2f}, RSI={snapshot.rsi:.1f}"
        )

    return Signal.HOLD, (
        f"No crossover — MA{config.MA_FAST}={snapshot.ma_fast:.2f}, "
        f"MA{config.MA_SLOW}={snapshot.ma_slow:.2f}, RSI={snapshot.rsi:.1f}"
    )
