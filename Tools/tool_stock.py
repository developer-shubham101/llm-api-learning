import yfinance as yf

def get_stock_price(symbol: str) -> dict:
    """Get the latest stock price for a given ticker symbol"""
    stock = yf.Ticker(symbol)
    data  = stock.history(period="1d")
    latest = data.iloc[-1]
    return {
        "symbol": symbol,
        "price":  round(latest["Close"], 2),
    }
