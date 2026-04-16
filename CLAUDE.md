# easy-trade2

A Python-based daily rule-driven trading system, designed to evolve from batch to real-time.

## Stack
- **Language**: Python 3.11+
- **Market data**: `yfinance` (Phase 1), Alpaca/Polygon websocket (Phase 2)
- **Broker**: Alpaca (`alpaca-py`) — paper trading first
- **Indicators**: `pandas`, `pandas-ta`
- **Scheduler**: cron / GitHub Actions (Phase 1), persistent process (Phase 2)
- **Storage**: SQLite for trade log

## Project Structure
```
easy-trade2/
├── data/
│   ├── snapshot.py       # MarketSnapshot dataclass — shared contract
│   ├── daily.py          # Phase 1: batch fetch via yfinance
│   └── stream.py         # Phase 2: websocket listener
├── rules/
│   ├── engine.py         # evaluate(snapshot) → Signal — never changes
│   └── basic.py          # MA crossover, RSI, MACD rules
├── execution/
│   └── orders.py         # submit orders to broker API
├── storage/
│   └── log.py            # SQLite trade log
├── scheduler/
│   ├── batch.py          # Phase 1 entry point (cron / GitHub Actions)
│   └── realtime.py       # Phase 2 entry point (persistent process)
├── analysis/             # Phase 2: AI/news enrichment
│   ├── news.py
│   └── agent.py
└── config.py             # tickers, thresholds, API keys (never hardcode keys)
```

## Architecture Principles
- `MarketSnapshot` is the stable interface between data sources and the rules engine
- Rules engine is **deterministic and stateless** — same input always produces same output
- Data layer is **swappable**: daily fetch (Phase 1) → websocket stream (Phase 2) without changing rules
- Orders are only placed after signal + risk check passes
- All trades are logged to SQLite with: date, ticker, action, quantity, price, reason

## Phases
- **Phase 1 (current)**: Daily batch — cron triggers at market open/close, fetches EOD data, evaluates rules, places orders
- **Phase 2**: Real-time — websocket stream replaces batch fetch, same rules engine, add news/sentiment agent as signal enrichment

## Key Conventions
- Config via environment variables, never hardcode API keys
- All rule functions signature: `def rule_name(snapshot: MarketSnapshot) -> Signal`
- Signal enum: `BUY`, `SELL`, `HOLD`
- Use paper trading (Alpaca sandbox) until rules are validated via backtesting
- Market timezone: America/New_York

## Dependencies
```
yfinance
pandas
pandas-ta
alpaca-py
python-dotenv
```
