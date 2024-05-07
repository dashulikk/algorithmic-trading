from typing import Optional
import yfinance as yf


def get_stock_price(stock: str) -> Optional[float]:
    """
    Fetches the latest closing stock price for a given stock symbol using yfinance.

    :param stock: The stock symbol to fetch the price for.
    :return: The latest closing stock price as a float. Returns None if data is not available.
    """
    ticker = yf.Ticker(stock)
    try:
        # Get the most recent day's data
        latest_data = ticker.history(period='1d')
        # Check if the data is not empty
        if not latest_data.empty:
            return latest_data['Close'].iloc[0]
        else:
            print("No data available for the specified stock symbol.")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
