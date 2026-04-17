import config
from data.snapshot import MarketSnapshot
from rules.engine import Signal


def execute(snapshot: MarketSnapshot, signal: Signal) -> str:
    """Place order based on signal. Returns action taken."""
    if not config.ALPACA_API_KEY:
        return "skipped — no Alpaca credentials configured"

    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import MarketOrderRequest
    from alpaca.trading.enums import OrderSide, TimeInForce

    client = TradingClient(config.ALPACA_API_KEY, config.ALPACA_SECRET_KEY, paper=True)
    account = client.get_account()
    cash = float(account.cash)

    # Check existing position
    qty_held = 0.0
    try:
        position = client.get_open_position(snapshot.ticker)
        qty_held = float(position.qty)
    except Exception:
        qty_held = 0.0

    if signal == Signal.BUY and qty_held == 0:
        qty = int((cash * config.MAX_POSITION_PCT) / snapshot.price)
        if qty < 1:
            return "skipped — insufficient cash"
        order = MarketOrderRequest(
            symbol=snapshot.ticker,
            qty=qty,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY,
        )
        client.submit_order(order)
        return f"BUY {qty} shares of {snapshot.ticker} @ ~${snapshot.price:.2f}"

    elif signal == Signal.SELL and qty_held > 0:
        order = MarketOrderRequest(
            symbol=snapshot.ticker,
            qty=int(qty_held),
            side=OrderSide.SELL,
            time_in_force=TimeInForce.DAY,
        )
        client.submit_order(order)
        return f"SELL {int(qty_held)} shares of {snapshot.ticker} @ ~${snapshot.price:.2f}"

    elif signal == Signal.BUY and qty_held > 0:
        return f"BUY signal but already holding {int(qty_held)} shares — skipped"

    elif signal == Signal.SELL and qty_held == 0:
        return "SELL signal but no position — skipped"

    return "HOLD — no action"
