import os
from dotenv import load_dotenv

load_dotenv()

# Tickers — S&P 100 (screening universe)
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

# Value screen thresholds (monthly screener — Graham-style)
VALUE_PE_MAX   = 15.0   # P/E < 15
VALUE_PB_MAX   = 1.5    # P/B < 1.5
VALUE_PFCF_MAX = 15.0   # P/FCF < 15
VALUE_DE_MAX   = 0.5    # Debt/Equity < 0.5
VALUE_ROE_MIN  = 0.10   # ROE > 10%
