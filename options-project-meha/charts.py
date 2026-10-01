"""
Step 6: Visualizations for the covered call backtest.

Produces two chart types per ticker:
  1. Equity curve: covered call strategy vs. buy-and-hold, over the test year
  2. Payoff diagram: illustrates the capped-upside mechanics of a single
     covered call trade at expiration

Saves everything as PNG files ready to drop into a README or write-up.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from backtest import run_backtest, pick_strike


def plot_equity_curve(log_df, ticker):
    strat_cum = (1 + log_df["strategy_period_return"]).cumprod()
    hold_cum = (1 + log_df["buyhold_period_return"]).cumprod()

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(log_df["exit_date"], strat_cum, marker="o", label="Covered Call Strategy", color="#1f6f4c")
    ax.plot(log_df["exit_date"], hold_cum, marker="o", label="Buy & Hold", color="#555555", linestyle="--")

    ax.set_title(f"{ticker}: Covered Call vs. Buy & Hold — Growth of $1", fontsize=13, fontweight="bold")
    ax.set_ylabel("Growth of $1")
    ax.set_xlabel("Date")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.autofmt_xdate(rotation=30)
    fig.tight_layout()

    filename = f"{ticker}_equity_curve.png"
    fig.savefig(filename, dpi=150)
    plt.close(fig)
    print(f"Saved {filename}")


def plot_payoff_diagram(entry_price, strike, premium_per_share, ticker):
    """
    Illustrates covered call P&L at expiration across a range of possible
    stock prices, vs. simply holding the stock uncovered.
    """
    price_range = np.linspace(entry_price * 0.7, entry_price * 1.3, 200)

    # Covered call P&L per share: stock gain (capped at strike) + premium
    stock_pnl = price_range - entry_price
    capped_pnl = np.minimum(price_range, strike) - entry_price
    covered_call_pnl = capped_pnl + premium_per_share

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(price_range, stock_pnl, label="Stock Only (Uncovered)", color="#555555", linestyle="--")
    ax.plot(price_range, covered_call_pnl, label="Covered Call", color="#1f6f4c", linewidth=2)

    ax.axvline(entry_price, color="gray", linestyle=":", alpha=0.6)
    ax.axvline(strike, color="orange", linestyle=":", alpha=0.8)
    ax.text(entry_price, ax.get_ylim()[1]*0.9, " Entry Price", rotation=90, va="top", fontsize=8)
    ax.text(strike, ax.get_ylim()[1]*0.9, " Strike", rotation=90, va="top", fontsize=8, color="orange")

    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title(f"{ticker}: Covered Call Payoff Diagram (at expiration)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Stock Price at Expiration ($)")
    ax.set_ylabel("Profit / Loss per Share ($)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()

    filename = f"{ticker}_payoff_diagram.png"
    fig.savefig(filename, dpi=150)
    plt.close(fig)
    print(f"Saved {filename}")


if __name__ == "__main__":
    for ticker in ["AAPL", "SPY"]:
        df = pd.read_csv(f"{ticker}_prices_vol.csv", skiprows=[1, 2], index_col=0)
        df.index.name = "Date"
        df.reset_index(inplace=True)
        df.rename(columns={df.columns[0]: "Date"}, inplace=True)
        df["close"] = pd.to_numeric(df["close"], errors="coerce")
        df["realized_vol"] = pd.to_numeric(df["realized_vol"], errors="coerce")
        df.dropna(subset=["close", "realized_vol"], inplace=True)

        log_df, summary = run_backtest(df)
        plot_equity_curve(log_df, ticker)

        # Use the first trade of the year as the illustrative payoff example
        first_trade = log_df.iloc[0]
        entry_price = first_trade["entry_price"]
        strike = first_trade["strike"]
        premium_per_share = first_trade["premium_collected"] / 100  # back out per-share premium
        plot_payoff_diagram(entry_price, strike, premium_per_share, ticker)
