"""
Step 5: Performance metrics for the covered call backtest.

Computes Sharpe ratio, max drawdown, and win rate for both the
covered call strategy and the buy-and-hold baseline, so we can
compare them on a risk-adjusted basis, not just raw dollar returns.
"""

import numpy as np
import pandas as pd

PERIODS_PER_YEAR = 252 / 21  # ~12 monthly periods, matching the 21-day holding period


def sharpe_ratio(period_returns, periods_per_year=PERIODS_PER_YEAR, risk_free_rate=0.045):
    """
    Annualized Sharpe ratio from a series of per-period returns.
    Subtracts the risk-free rate (converted to a per-period rate) before annualizing.
    """
    period_returns = np.array(period_returns)
    rf_per_period = risk_free_rate / periods_per_year
    excess_returns = period_returns - rf_per_period

    if excess_returns.std() == 0:
        return np.nan

    return (excess_returns.mean() / excess_returns.std()) * np.sqrt(periods_per_year)


def max_drawdown(period_returns):
    """
    Max drawdown from a series of per-period returns, computed on the
    resulting cumulative equity curve (starting at 1.0).
    """
    cumulative = (1 + np.array(period_returns)).cumprod()
    running_max = np.maximum.accumulate(cumulative)
    drawdowns = (cumulative - running_max) / running_max
    return drawdowns.min()  # most negative value = the max drawdown


def win_rate(period_returns):
    """% of periods with a positive return."""
    period_returns = np.array(period_returns)
    return (period_returns > 0).mean()


def summarize_performance(log_df, label=""):
    strat_returns = log_df["strategy_period_return"].values
    hold_returns = log_df["buyhold_period_return"].values

    print(f"\n--- {label} Performance Metrics ---")
    print(f"{'Metric':<25}{'Covered Call':>15}{'Buy & Hold':>15}")
    print(f"{'Sharpe Ratio':<25}{sharpe_ratio(strat_returns):>15.2f}{sharpe_ratio(hold_returns):>15.2f}")
    print(f"{'Max Drawdown':<25}{max_drawdown(strat_returns):>15.2%}{max_drawdown(hold_returns):>15.2%}")
    print(f"{'Win Rate':<25}{win_rate(strat_returns):>15.2%}{win_rate(hold_returns):>15.2%}")


if __name__ == "__main__":
    from backtest import run_backtest

    for ticker in ["AAPL", "SPY"]:
        df = pd.read_csv(f"{ticker}_prices_vol.csv", skiprows=[1, 2], index_col=0)
        df.index.name = "Date"
        df.reset_index(inplace=True)
        df.rename(columns={df.columns[0]: "Date"}, inplace=True)
        df["close"] = pd.to_numeric(df["close"], errors="coerce")
        df["realized_vol"] = pd.to_numeric(df["realized_vol"], errors="coerce")
        df.dropna(subset=["close", "realized_vol"], inplace=True)

        log_df, summary = run_backtest(df)
        summarize_performance(log_df, label=ticker)
