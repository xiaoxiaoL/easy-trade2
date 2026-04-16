import os
from dotenv import load_dotenv

load_dotenv()

# Tickers to trade
TICKERS = ["SPY"]

# MA crossover
MA_FAST = 5
MA_SLOW = 20

# RSI
RSI_PERIOD = 14
RSI_BUY_THRESHOLD = 50   # RSI must be above this to confirm BUY
RSI_SELL_THRESHOLD = 50  # RSI must be below this to confirm SELL

# Broker (Alpaca paper trading)
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")
ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
