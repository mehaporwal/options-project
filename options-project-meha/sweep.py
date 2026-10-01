"""
Step 7: Strike-distance sweep.

Runs the covered call backtest across multiple strike distances
(2%, 5%, 10% OTM) for both tickers, so we can see how strike
selection trades off raw return, risk-adjusted return, and
assignment frequency.
"""

import pandas as pd
import matplotlib.pyplot as plt

from backtest import run_backtest
from metrics import sharpe_ratio, max_drawdown, win_rate

OTM_LEVELS = [0.02, 0.05, 0.10]  # 2%, 5%, 10% out-of-the-money


def load_price_data(ticker):
    df = pd.read_csv(f"{ticker}_prices_vol.csv", skiprows=[1, 2], index_col=0)
    df.index.name = "Date"
    df.reset_index(inplace=True)
    df.rename(columns={df.columns[0]: "Date"}, inplace=True)
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df["realized_vol"] = pd.to_numeric(df["realized_vol"], errors="coerce")
    df.dropna(subset=["close", "realized_vol"], inplace=True)
    return df


def run_sweep(ticker):
    df = load_price_data(ticker)
    results = []

    for otm_pct in OTM_LEVELS:
        log_df, summary = run_backtest(df, otm_pct=otm_pct)
        strat_returns = log_df["strategy_period_return"].values

        results.append({
            "ticker": ticker,
            "otm_pct": f"{otm_pct:.0%}",
            "num_called_away": summary["num_called_away"],
            "total_premiums_$": summary["total_premiums_collected_$"],
            "outperformance_$": summary["outperformance_$"],
            "sharpe_ratio": sharpe_ratio(strat_returns),
            "max_drawdown": max_drawdown(strat_returns),
            "win_rate": win_rate(strat_returns),
        })

    return pd.DataFrame(results)


def plot_sweep(sweep_df, ticker):
    fig, ax1 = plt.subplots(figsize=(8, 5))

    ax1.bar(sweep_df["otm_pct"], sweep_df["sharpe_ratio"], color="#1f6f4c", alpha=0.8, label="Sharpe Ratio")
    ax1.set_ylabel("Sharpe Ratio", color="#1f6f4c")
    ax1.set_xlabel("Strike Distance (% OTM)")
    ax1.tick_params(axis="y", labelcolor="#1f6f4c")

    ax2 = ax1.twinx()
    ax2.plot(sweep_df["otm_pct"], sweep_df["num_called_away"], color="orange", marker="o", linewidth=2, label="# Called Away")
    ax2.set_ylabel("# Times Called Away", color="orange")
    ax2.tick_params(axis="y", labelcolor="orange")

    ax1.set_title(f"{ticker}: Sharpe Ratio vs. Assignment Frequency by Strike Distance", fontsize=12, fontweight="bold")
    fig.tight_layout()

    filename = f"{ticker}_strike_sweep.png"
    fig.savefig(filename, dpi=150)
    plt.close(fig)
    print(f"Saved {filename}")


if __name__ == "__main__":
    all_results = []
    for ticker in ["AAPL", "SPY"]:
        sweep_df = run_sweep(ticker)
        print(f"\n=== {ticker} Strike Distance Sweep ===")
        print(sweep_df.to_string(index=False))
        plot_sweep(sweep_df, ticker)
        all_results.append(sweep_df)

    pd.concat(all_results, ignore_index=True).to_csv("strike_sweep_results.csv", index=False)
    print("\nSaved combined results to strike_sweep_results.csv")
