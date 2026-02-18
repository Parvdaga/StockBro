"""
Static knowledge base for Indian stock market terms, sectors, and common queries.
Provides a fallback and educational layer for the AI.
"""

KNOWLEDGE_BASE = {
    "terms": {
        "IPO": "Initial Public Offering (IPO) is the process by which a private company can go public by sale of its stocks to general public.",
        "F&O": "Futures and Options are derivative instruments where you trade the future value of an underlying asset like a stock or index.",
        "NIFTY 50": "The NIFTY 50 is a benchmark Indian stock market index that represents the weighted average of 50 of the largest Indian companies listed on the NSE.",
        "SENSEX": "The S&P BSE SENSEX is a stock market index of 30 well-established and financially sound companies listed on the Bombay Stock Exchange.",
        "LTP": "Last Traded Price (LTP) is the price at which the last transaction for a particular stock took place.",
        "Dividend": "A dividend is a distribution of profits by a corporation to its shareholders.",
        "Market Cap": "Market Capitalization is the total value of a company's shares of stock (Price x Total Shares).",
    },
    "sectors": {
        "Banking": ["HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "AXISBANK"],
        "IT": ["TCS", "INFY", "HCLTECH", "WIPRO", "TECHM"],
        "Defense": ["HAL", "BEL", "MAZDOCK", "BDL", "COCHINSHIP"],
        "Automobile": ["TATAMOTORS", "MARUTI", "M&M", "HEROMOTOCO", "EICHERMOT"],
        "Energy": ["RELIANCE", "ONGC", "NTPC", "POWERGRID", "BPCL"],
        "Pharma": ["SUNPHARMA", "CIPLA", "DRREDDY", "DIVISLAB", "APOLLOHOSP"],
        "Consumer": ["ITC", "HINDUNILVR", "NESTLEIND", "BRITANNIA", "TATACONSUM"],
    },
    "strategies": {
        "Intraday": "Buying and selling stocks within the same trading day to capitalize on short-term price movements.",
        "Long Term": "Investing in stocks for a period of several years, focusing on fundamental growth and compounding.",
        "Value Investing": "Buying stocks that appear to be trading for less than their intrinsic or book value.",
    }
}

def get_knowledge(category: str, key: str = None) -> str:
    """Retrieve information from the knowledge base."""
    cat_data = KNOWLEDGE_BASE.get(category, {})
    if key:
        return cat_data.get(key, f"No information found for '{key}' in '{category}'.")
    return cat_data
