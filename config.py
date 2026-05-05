import os
from dotenv import load_dotenv

load_dotenv()

# Tickers to trade — S&P 100 (largest 100 US stocks)
TICKERS = [
    "AAPL", "ABBV", "ABT", "ACN", "ADBE", "AIG", "AMD", "AMGN", "AMT", "AMZN",
    "AXP", "BA", "BAC", "BK", "BKNG", "BLK", "BMY", "BRK-B", "C", "CAT",
    "CHTR", "CL", "CMCSA", "COF", "COP", "COST", "CRM", "CSCO", "CVS", "CVX",
    "DHR", "DIS", "DOW", "DUK", "EMR", "EXC", "F", "FDX", "GD", "GE",
    "GILD", "GM", "GOOG", "GS", "HD", "HON", "IBM", "INTC", "INTU", "JNJ",
    "JPM", "KHC", "KO", "LIN", "LLY", "LMT", "LOW", "MA", "MCD", "MDLZ",
    "MDT", "MET", "META", "MMM", "MO", "MRK", "MS", "MSFT", "NEE", "NFLX",
    "NKE", "NVDA", "ORCL", "OXY", "PEP", "PFE", "PG", "PM", "PYPL", "QCOM",
    "RTX", "SBUX", "SCHW", "SO", "SPG", "T", "TGT", "TMO", "TMUS", "TXN",
    "UNH", "UNP", "UPS", "USB", "V", "VZ", "WFC", "WMT", "XOM", "TRV",
]

# RSI
RSI_PERIOD = 14

# Value investing thresholds
PE_MAX = 25.0        # max trailing P/E to qualify as undervalued
RSI_OVERSOLD = 35    # entry: stock is beaten down
RSI_OVERBOUGHT = 90  # exit: strongly overbought — hold longer for better returns
STOP_LOSS = 0.15           # exit: cut position if down 15% from buy price
STOP_LOSS_COOLDOWN = 30    # days to wait before re-entering after a stop-loss

# Value screen thresholds (monthly screener — Graham-style)
VALUE_PE_MAX   = 15.0   # P/E < 15
VALUE_PB_MAX   = 1.5    # P/B < 1.5
VALUE_PFCF_MAX = 15.0   # P/FCF < 15
VALUE_DE_MAX   = 0.5    # Debt/Equity < 0.5
VALUE_ROE_MIN  = 0.10   # ROE > 10%

# Position sizing
MAX_POSITIONS = 10       # max simultaneous holdings
MAX_POSITION_PCT = 0.10  # 10% of cash per trade (sized for 10 positions)

# Broker (Alpaca paper trading)
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")
ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
