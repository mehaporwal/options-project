"""
Step 3: Black-Scholes pricing for a European call option.

We use this to simulate what the premium would have been for selling
a covered call on any given day, using that day's stock price and
realized volatility (as a stand-in for implied volatility).
"""

import numpy as np
from scipy.stats import norm

RISK_FREE_RATE = 0.045  # ~4.5%, approximating recent short-term T-bill yields


def black_scholes_call_price(S, K, T, r, sigma):
    """
    S: current stock price
    K: strike price
    T: time to expiration, in YEARS (e.g. 30 days = 30/365)
    r: risk-free rate (annualized)
    sigma: volatility (annualized)

    Returns the theoretical price (premium) of one call option, per share.
    Multiply by 100 to get the premium for a full contract.
    """
    if T <= 0 or sigma <= 0:
        return max(S - K, 0)  # option has no time value left

    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    return call_price


def pick_strike(S, otm_pct=0.05):
    """
    Picks a strike price a fixed % above the current stock price.
    otm_pct=0.05 means 5% out-of-the-money, a common covered call choice.
    """
    return S * (1 + otm_pct)


if __name__ == "__main__":
    # Quick sanity check using the AAPL numbers you just pulled
    S = 253.10       # current AAPL price
    sigma = 0.2165   # realized_vol from your data
    T = 30 / 365      # 30-day covered call
    K = pick_strike(S, otm_pct=0.05)

    premium_per_share = black_scholes_call_price(S, K, T, RISK_FREE_RATE, sigma)
    premium_per_contract = premium_per_share * 100

    print(f"Stock price (S): ${S:.2f}")
    print(f"Strike (K, 5% OTM): ${K:.2f}")
    print(f"Volatility (sigma): {sigma:.2%}")
    print(f"Premium per share: ${premium_per_share:.2f}")
    print(f"Premium per contract (x100 shares): ${premium_per_contract:.2f}")
