import sqlite3

from data.snapshot import MarketSnapshot
from rules.engine import Signal

DB_PATH = "trades.db"


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS signals (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                date      TEXT,
                ticker    TEXT,
                signal    TEXT,
                price     REAL,
                pe_ratio  REAL,
                pb_ratio  REAL,
                rsi       REAL,
                reason    TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def log_signal(snapshot: MarketSnapshot, signal: Signal, reason: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO signals (date, ticker, signal, price, pe_ratio, pb_ratio, rsi, reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(snapshot.date),
            snapshot.ticker,
            signal.value,
            snapshot.price,
            snapshot.pe_ratio,
            snapshot.pb_ratio,
            snapshot.rsi,
            reason,
        ))
