"""
Step 4: Covered call backtesting engine.

Rolls a new ~30-day covered call every month using the Black-Scholes
premium, tracks whether shares get "called away," and compares total
strategy return to a simple buy-and-hold approach.
"""

import pandas as pd
import numpy as np
from black_scholes import black_scholes_call_price, pick_strike, RISK_FREE_RATE

SHARES = 100
HOLDING_PERIOD_DAYS = 21  # ~30 calendar days ≈ 21 trading days
OTM_PCT = 0.05


def run_backtest(price_df, otm_pct=OTM_PCT, holding_period=HOLDING_PERIOD_DAYS):
    price_df = price_df.reset_index()
    n = len(price_df)

    cash_from_premiums = 0.0
    assignment_cash_adjustment = 0.0
    shares_held = SHARES
    trade_log = []

    i = 0
    while i + holding_period < n:
        entry_row = price_df.iloc[i]
        exit_row = price_df.iloc[i + holding_period]

        S = entry_row["close"]
        sigma = entry_row["realized_vol"]
        T = holding_period / 252  # trading-day fraction of a year
        K = pick_strike(S, otm_pct)

        premium_per_share = black_scholes_call_price(S, K, T, RISK_FREE_RATE, sigma)
        premium_collected = premium_per_share * shares_held
        cash_from_premiums += premium_collected

        exit_price = exit_row["close"]
        called_away = exit_price > K

        if called_away:
            # shares sold at strike, then repurchased at market to continue strategy
            sale_proceeds = K * shares_held
            buyback_cost = exit_price * shares_held
            assignment_cash_adjustment += (sale_proceeds - buyback_cost)

        trade_log.append({
            "entry_date": entry_row["Date"],
            "exit_date": exit_row["Date"],
            "entry_price": S,
            "strike": K,
            "exit_price": exit_price,
            "premium_collected": premium_collected,
            "called_away": called_away,
            "strategy_period_return": (
                ((K if called_away else exit_price) * shares_held + premium_collected)
                / (S * shares_held) - 1
            ),
            "buyhold_period_return": exit_price / S - 1,
        })

        i += holding_period

    log_df = pd.DataFrame(trade_log)

    first_price = price_df.iloc[0]["close"]
    last_price = price_df.iloc[min(i, n - 1)]["close"]

    buy_and_hold_return = (last_price - first_price) * SHARES
    total_premiums = log_df["premium_collected"].sum() if len(log_df) else 0.0
    covered_call_return = buy_and_hold_return + total_premiums + assignment_cash_adjustment

    summary = {
        "num_trades": len(log_df),
        "num_called_away": int(log_df["called_away"].sum()) if len(log_df) else 0,
        "total_premiums_collected_$": total_premiums,
        "assignment_cash_adjustment_$": assignment_cash_adjustment,
        "buy_and_hold_return_$": buy_and_hold_return,
        "covered_call_return_$": covered_call_return,
        "outperformance_$": covered_call_return - buy_and_hold_return,
    }

    return log_df, summary


if __name__ == "__main__":
    for ticker in ["AAPL", "SPY"]:
        print(f"\n===== {ticker} Covered Call Backtest =====")
        df = pd.read_csv(f"{ticker}_prices_vol.csv", skiprows=[1, 2], index_col=0)
        df.index.name = "Date"
        df.reset_index(inplace=True)
        df.rename(columns={df.columns[0]: "Date"}, inplace=True)
        df["close"] = pd.to_numeric(df["close"], errors="coerce")
        df["realized_vol"] = pd.to_numeric(df["realized_vol"], errors="coerce")
        df.dropna(subset=["close", "realized_vol"], inplace=True)

        log_df, summary = run_backtest(df)

        print(log_df.to_string(index=False))
        print("\nSummary:")
        for k, v in summary.items():
            print(f"  {k}: {v:,.2f}" if isinstance(v, float) else f"  {k}: {v}")
