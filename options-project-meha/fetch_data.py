"""
Step 2: Source historical price data for the covered call backtest.

Since free historical *options* data isn't available, we pull historical
*stock* price data and compute realized volatility from it. This volatility
feeds into a Black-Scholes model later to simulate what covered call
premiums would have been.
"""

import yfinance as yf
import pandas as pd
import numpy as np

TICKERS = ["AAPL", "SPY"]
PERIOD = "1y"  # 1 year of daily data

def fetch_price_data(ticker, period=PERIOD):
    data = yf.download(ticker, period=period, interval="1d", progress=False, auto_adjust=True)
    data = data[["Close"]].rename(columns={"Close": "close"})
    data.dropna(inplace=True)
    return data

def compute_realized_volatility(price_df, window=21):
    """
    Computes annualized rolling realized volatility from daily returns.
    window=21 trading days ≈ 1 month, a common choice for monthly covered calls.
    """
    price_df = price_df.copy()
    price_df["log_return"] = np.log(price_df["close"] / price_df["close"].shift(1))
    price_df["realized_vol"] = price_df["log_return"].rolling(window).std() * np.sqrt(252)
    return price_df.dropna()

if __name__ == "__main__":
    all_data = {}
    for ticker in TICKERS:
        print(f"Fetching {ticker}...")
        prices = fetch_price_data(ticker)
        prices_with_vol = compute_realized_volatility(prices)
        all_data[ticker] = prices_with_vol
        print(prices_with_vol.tail())
        prices_with_vol.to_csv(f"{ticker}_prices_vol.csv")
        print(f"Saved {ticker}_prices_vol.csv ({len(prices_with_vol)} rows)\n")
