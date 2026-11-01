"""Educational ASX momentum backtest (not investment advice).

Uses a fixed, present-day stock list and historical prices. Results can suffer
from survivorship/selection bias and should not be treated as live evidence.
"""

import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

START_DATE = "2015-01-01"
END_DATE = "2025-01-01"  # Exclusive
LOOKBACK = 252           # About 12 trading months
SKIP = 21                # Exclude the latest trading month
TOP_N_VALUES = (10, 20, 30)
COST_RATE = 0.001        # Illustrative cost per $1 traded (one way)
TRADING_DAYS = 252

TICKERS = [
    "BHP.AX", "CBA.AX", "CSL.AX", "NAB.AX", "WBC.AX", "ANZ.AX",
    "WES.AX", "WOW.AX", "TLS.AX", "RIO.AX", "MQG.AX", "TCL.AX",
    "FMG.AX", "GMG.AX", "STO.AX", "ORG.AX", "QBE.AX", "SUN.AX",
    "IAG.AX", "ASX.AX", "GPT.AX", "BXB.AX", "JHX.AX", "ALL.AX",
    "REA.AX", "SEK.AX", "CPU.AX", "APA.AX", "AGL.AX", "ORI.AX",
    "IPL.AX", "LLC.AX", "SGP.AX", "BEN.AX", "BOQ.AX", "COH.AX",
    "RHC.AX", "SHL.AX",
]


def download_closes(symbols):
    """Return a date-by-ticker table of adjusted daily close prices."""
    raw = yf.download(symbols, start=START_DATE, end=END_DATE,
                      auto_adjust=True, group_by="column", progress=False,
                      threads=False)
    if raw.empty:
        raise RuntimeError("No prices downloaded. Check your internet connection.")
    if isinstance(raw.columns, pd.MultiIndex):
        prices = raw["Close"]
    else:
        prices = raw[["Close"]].rename(columns={"Close": symbols[0]})
    return prices.sort_index().dropna(axis=1, how="all")


def metrics(daily_returns):
    r = daily_returns.dropna()
    if len(r) < 2:
        raise ValueError("Not enough returns to calculate metrics.")
    equity = (1 + r).cumprod()
    years = len(r) / TRADING_DAYS
    std = r.std()
    peak = pd.concat([pd.Series([1.0]), equity.reset_index(drop=True)]).cummax().iloc[1:].to_numpy()
    return {
        "Total return": equity.iloc[-1] - 1,
        "Annual return (CAGR)": equity.iloc[-1] ** (1 / years) - 1,
        "Annual volatility": std * np.sqrt(TRADING_DAYS),
        # Assumes zero risk-free rate; explain this in project documentation.
        "Sharpe (rf=0)": (r.mean() / std * np.sqrt(TRADING_DAYS)) if std > 0 else np.nan,
        "Maximum drawdown": np.min(equity.to_numpy() / peak - 1),
    }


def backtest(prices, top_n):
    # A signal at date t uses only closes from t-21 or earlier.
    momentum = prices.shift(SKIP) / prices.shift(LOOKBACK) - 1
    dates = prices.groupby(prices.index.year).tail(1).index
    out = []
    previous_weights = pd.Series(dtype=float)

    for start, end in zip(dates[:-1], dates[1:]):
        score = momentum.shift(1).loc[start].dropna().sort_values(ascending=False)
        # Require continuous prices through each holding period so missing data
        # cannot silently become a zero return or an unpriced liquidation.
        good = score.index[prices.loc[start, score.index].notna()]
        score = score.loc[good]

        selected = list(score.head(top_n).index)
        if len(selected) < top_n:
            print(f"Skipping {start.date()}: only {len(selected)} valid stocks for top {top_n}")
            continue

        # Equal-weight at rebalance; positions drift until next rebalance.
        weights = pd.Series(1 / top_n, index=selected)
        old = previous_weights.reindex(previous_weights.index.union(weights.index), fill_value=0)
        new = weights.reindex(old.index, fill_value=0)
        traded_dollars = (new - old).abs().sum()
        # Convert to a portfolio-level charge at the start of the period.
        cost = COST_RATE * traded_dollars

        period_prices = prices.loc[(prices.index >= start) & (prices.index <= end), selected]
        if period_prices.isna().any().any():
            missing = period_prices.columns[
                period_prices.isna().any()
            ].tolist()
            raise ValueError(
                f"Missing prices during holding period starting {start.date()}: {missing}"
            )
        relatives = period_prices.div(period_prices.iloc[0])
        period_equity = relatives.mul(weights).sum(axis=1)
        period_returns = period_equity.pct_change().iloc[1:]
        period_returns.iloc[0] = (1 + period_returns.iloc[0]) * (1 - cost) - 1
        out.append(period_returns)

        # End-of-period drifted weights, for next period's turnover estimate.
        end_values = weights * relatives.iloc[-1]
        previous_weights = end_values / end_values.sum()

    if not out:
        raise RuntimeError("No valid holding periods. Inspect price coverage and tickers.")
    return pd.concat(out).sort_index()


def main():
    prices = download_closes(TICKERS)
    print(f"Downloaded {len(prices.columns)} stocks with price data.")
    strategies = {n: backtest(prices, n) for n in TOP_N_VALUES}
    # ^AXJO is a price index; it may exclude dividends and differs from an
    # adjusted stock-price portfolio. This benchmark is illustrative only.
    benchmark_prices = download_closes(["IOZ.AX"])["IOZ.AX"]
    common_dates = strategies[20].index.intersection(benchmark_prices.index)
    benchmark = benchmark_prices.pct_change().loc[common_dates].dropna()
    all_series = {f"Top {n}": r.loc[common_dates] for n, r in strategies.items()}
    all_series["IOZ ETF (adjusted)"] = benchmark
    # Compare using identical dates for all series.
    shared_dates = benchmark.index
    for r in strategies.values():
        shared_dates = shared_dates.intersection(r.index)
    all_series = {name: r.loc[shared_dates] for name, r in all_series.items()}
    summary = pd.DataFrame({name: metrics(r) for name, r in all_series.items()}).T
    print("\nPerformance summary (illustrative):")
    print(summary.round(4).to_string())
    summary.to_csv("strategy_results.csv")
    plt.figure(figsize=(11, 6))
    for name, r in all_series.items():
        plt.plot((1 + r).cumprod(), label=name)
    plt.title("ASX momentum strategy (illustrative backtest)")
    plt.ylabel("Growth of $1")
    plt.xlabel("Date")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("momentum_chart.png", dpi=160)
    plt.show()
    print("\nSaved strategy_results.csv and momentum_chart.png")
    print(
    "Caution: fixed stock universe, historical data, "
    "and ETF benchmark limitations may affect results."
)


if __name__ == "__main__":
    main()
