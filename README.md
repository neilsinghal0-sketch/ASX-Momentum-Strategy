# ASX Momentum Trading Strategy

## Project Overview

This project develops and backtests a momentum-based investment strategy using historical Australian Securities Exchange (ASX) stock data.

The objective is to investigate whether selecting stocks with strong historical momentum can outperform a broad Australian equity-market benchmark.

The project compares equally weighted portfolios containing 10, 20 and 30 stocks against the iShares Core S&P/ASX 200 ETF (IOZ).

## Strategy Methodology

1. Download historical adjusted stock prices using Python and `yfinance`.
2. Calculate approximately 12-month price momentum, excluding the most recent 21 trading days.
3. Rank stocks according to their momentum scores.
4. Select the highest-ranked stocks for each portfolio.
5. Rebalance annually using signals from the previous trading day.
6. Calculate compounded portfolio returns, incorporating illustrative transaction costs.

Portfolio weights are initially equal and subsequently drift with market movements until the next rebalance.

## Performance Metrics

The backtest calculates:

- **CAGR:** Compound annual growth rate.
- **Annualised volatility:** Standard deviation of returns, scaled to one year.
- **Sharpe ratio:** Risk-adjusted return, using a 0% risk-free rate for this illustration.
- **Maximum drawdown:** Largest historical peak-to-trough portfolio decline.

## Benchmark

The strategy is compared against the IOZ ETF using adjusted historical prices, providing an approximate dividend-inclusive Australian equity-market benchmark.

## Limitations

This is an educational backtest, not a validated trading strategy.

- The fixed stock universe introduces survivorship bias.
- Historical prices may contain missing or inaccurate data.
- Execution at closing prices is assumed.
- Trading costs and market impact are simplified.
- Historical performance does not predict future returns.

## Technologies

Python, pandas, NumPy, yfinance and Matplotlib.

## Running the Project

Install dependencies:

```bash
pip install pandas numpy yfinance matplotlib
```

Run:

```bash
python momentum_backtest_clean.py
```

The script generates a performance summary, a CSV results file and a portfolio growth chart.