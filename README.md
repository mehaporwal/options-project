# Covered Call Options Strategy — Backtest & Risk-Adjusted Performance Analysis

A from-scratch backtesting engine that simulates a rolling covered call strategy on AAPL and SPY, using Black-Scholes option pricing on real historical price and volatility data. Compares strategy performance against a simple buy-and-hold baseline across both raw returns and risk-adjusted metrics.

## Motivation

Covered calls are a widely used income-generating options strategy, but their real value proposition — smoother, more consistent returns in exchange for capped upside — is often better shown than described. This project quantifies that trade-off empirically using a full year of real market data, rather than relying on theoretical claims.

## Methodology

**1. Data**
Historical daily closing prices for AAPL and SPY were pulled via `yfinance` over a 1-year window. Rolling 21-trading-day (≈1 month) realized volatility was computed from daily log returns and annualized, serving as a proxy for implied volatility.

**2. Option Pricing**
Since free historical *options* data isn't available, monthly call option premiums were priced using the **Black-Scholes model**, using each period's actual stock price and realized volatility, a fixed risk-free rate (4.5%, approximating recent T-bill yields), and a strike set 5% out-of-the-money.

**3. Backtest Logic**
Starting with 100 hypothetical shares, the strategy rolls a new ~30-day covered call every period:
- If the stock closes below the strike at expiration → the call expires worthless, the premium is kept, shares are retained.
- If the stock closes above the strike → shares are "called away" at the strike price, then immediately repurchased at market to continue the strategy into the next period.

**4. Performance Metrics**
Alongside raw dollar returns, the strategy was evaluated on:
- **Sharpe Ratio** — risk-adjusted return, annualized
- **Max Drawdown** — largest peak-to-trough decline in the equity curve
- **Win Rate** — % of periods with a positive return

## Results

| Metric | AAPL — Covered Call | AAPL — Buy & Hold | SPY — Covered Call | SPY — Buy & Hold |
|---|---|---|---|---|
| Trades | 10 | — | 10 | — |
| Called Away | 1 (10%) | — | 4 (40%) | — |
| Premiums Collected | $1,679.75 | — | $2,948.83 | — |
| Total Return ($) | $10,591.29 | $10,684.48 | $4,800.29 | $4,914.50 |
| Outperformance | **-$93.19** | — | **-$114.20** | — |
| Sharpe Ratio | **1.17** | 0.91 | **1.64** | 1.44 |
| Max Drawdown | **-6.45%** | -7.64% | **-3.77%** | -4.04% |
| Win Rate | 70% | 70% | **70%** | 60% |

### Equity Curves
![AAPL Equity Curve](AAPL_equity_curve.png)
![SPY Equity Curve](SPY_equity_curve.png)

### Payoff Diagrams
![AAPL Payoff Diagram](AAPL_payoff_diagram.png)
![SPY Payoff Diagram](SPY_payoff_diagram.png)

### Strike Distance Sweep

The base results above use a single 5% out-of-the-money strike. To understand how sensitive the strategy is to strike selection, the backtest was re-run across three strike distances (2%, 5%, 10% OTM) for both tickers.

| Ticker | Strike | Called Away | Premiums | Outperformance | Sharpe | Max Drawdown | Win Rate |
|---|---|---|---|---|---|---|---|
| AAPL | 2% OTM | 5/10 | $5,435.62 | -$1,184.66 | 1.07 | -6.97% | 70% |
| AAPL | 5% OTM | 4/10 | $2,948.83 | -$114.20 | **1.17** | -6.45% | 70% |
| AAPL | 10% OTM | 1/10 | $957.58 | -$35.80 | 1.01 | -7.23% | 70% |
| SPY | 2% OTM | 4/10 | $5,753.78 | **+$385.94** | **2.15** | -2.93% | **90%** |
| SPY | 5% OTM | 1/10 | $1,679.75 | -$93.19 | 1.64 | -3.77% | 70% |
| SPY | 10% OTM | 0/10 | $156.83 | +$156.83 | 1.45 | -4.03% | 60% |

![AAPL Strike Sweep](AAPL_strike_sweep.png)
![SPY Strike Sweep](SPY_strike_sweep.png)

**Optimal strike selection is asset-dependent.** For AAPL, wider strikes (5–10% OTM) performed better — its larger, more volatile rallies meant tighter strikes got capped too often, giving up more upside than the extra premium was worth. For SPY, the opposite held: the tightest strike (2% OTM) was best on every metric, including a positive outperformance vs. buy-and-hold — SPY's steadier, lower-volatility climb meant frequent premium collection consistently outweighed the smaller, more contained capped gains. No single strike distance dominates across both assets; strike selection should account for the underlying's volatility profile.

## Key Findings

Over this 1-year, broadly bullish test window, the covered call strategy **underperformed buy-and-hold on raw dollar returns** for both tickers at the base 5% OTM strike (-$93 AAPL, -$114 SPY) — driven by shares being called away during strong upward moves and capping further gains.

However, on a **risk-adjusted basis, the strategy outperformed buy-and-hold on every metric measured** at the base strike: higher Sharpe ratios (1.17 vs 0.91 for AAPL, 1.64 vs 1.44 for SPY), smaller max drawdowns, and an improved win rate on SPY (70% vs 60%).

The **strike distance sweep** revealed a further, asset-dependent nuance: the best strike distance was not the same for both tickers. AAPL performed best with a wider 5% OTM strike, since its larger rallies made tighter strikes too costly to cap. SPY performed best with the tightest strike tested (2% OTM), since its steadier climb let frequent premium collection outweigh the smaller capped gains — even beating buy-and-hold outright (+$386, Sharpe 2.15, 90% win rate). This confirms the core trade-off covered calls are known for — smoother, more consistent returns in exchange for capped upside — while showing that the optimal strike distance depends on the underlying asset's volatility profile, not a one-size-fits-all rule.

## Limitations

- Option premiums are Black-Scholes estimates using realized (not implied) volatility, since historical options chain data isn't freely available. Real-world premiums may differ, particularly around earnings or other IV-inflating events.
- No transaction costs, bid-ask spreads, or slippage are modeled.
- Assumes European-style exercise at expiration only (no early assignment).
- Single strike selection rule (5% OTM) — results would vary with different strike distances or expiration lengths.

## Tech Stack

Python, pandas, NumPy, SciPy (Black-Scholes), Matplotlib, yfinance

## How to Run

```bash
pip install yfinance pandas numpy scipy matplotlib

python fetch_data.py    # pulls price + volatility data
python backtest.py      # runs the backtest, prints trade log + summary
python metrics.py       # prints Sharpe ratio, max drawdown, win rate
python charts.py        # generates equity curve + payoff diagram PNGs
python sweep.py         # runs the strike-distance sweep, prints table + saves charts/CSV
```
