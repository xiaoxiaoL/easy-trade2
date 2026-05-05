import config
from data.snapshot import MarketSnapshot
from rules.engine import Signal


def undervalued_rsi(snapshot: MarketSnapshot, buy_price: float = 0.0) -> tuple[Signal, str]:
    """BUY when P/E is low and RSI is oversold. SELL when RSI is overbought or stop-loss hit."""
    pe_ok = 0 < snapshot.pe_ratio <= config.PE_MAX

    # Stop-loss check (only if we hold a position)
    if buy_price > 0:
        loss_pct = (snapshot.price - buy_price) / buy_price
        if loss_pct <= -config.STOP_LOSS:
            return Signal.SELL, (
                f"Stop-loss hit: price={snapshot.price:.2f}, buy={buy_price:.2f}, "
                f"loss={loss_pct*100:.1f}%"
            )

    if snapshot.rsi >= config.RSI_OVERBOUGHT:
        return Signal.SELL, (
            f"RSI overbought: RSI={snapshot.rsi:.1f}"
        )

    if pe_ok and snapshot.rsi <= config.RSI_OVERSOLD:
        return Signal.BUY, (
            f"Undervalued + oversold: P/E={snapshot.pe_ratio:.1f}, RSI={snapshot.rsi:.1f}"
        )

    return Signal.HOLD, (
        f"No signal — P/E={snapshot.pe_ratio:.1f}, RSI={snapshot.rsi:.1f}"
    )
