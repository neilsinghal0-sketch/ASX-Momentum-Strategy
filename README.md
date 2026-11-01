# ASX Momentum Trading Strategy

## Project Overview

I built this project to explore momentum investing and get a better understanding of how trading strategies can be tested using Python.

The strategy ranks ASX stocks based on their performance over the previous year, excluding the most recent month. I tested portfolios of 10, 20 and 30 stocks to see how the number of holdings affects returns and risk.

I also compared the results against the IOZ ETF, which provides exposure to the ASX 200.

One limitation of this project is that it uses a fixed list of stocks, which can introduce survivorship bias. The results are therefore useful for exploring the strategy, but shouldn't be treated as evidence that it would outperform in real trading.

Install dependencies:

```bash
pip install pandas numpy yfinance matplotlib
```

Run:

```bash
python momentum_backtest_clean.py
```

The script generates a performance summary, a CSV results file and a portfolio growth chart.

## Backtest Performance

![ASX Momentum Strategy Performance](momentum%20chart.png)

### Backtest Results (2015–2025)

| Portfolio | CAGR | Sharpe Ratio |
|---|---:|---:|
| Top 10 Momentum | 14.12% | 0.8585 |
| Top 20 Momentum | 12.55% | 0.8418 |
| Top 30 Momentum | 11.69% | 0.8129 |
| IOZ ETF Benchmark | 9.04% | 0.6625 |

## What I Learned

Working on this project helped me understand how momentum strategies are constructed and evaluated.

I became more familiar with calculating portfolio returns, volatility, Sharpe ratios and maximum drawdowns. I also learned how important it is to account for transaction costs and avoid biases when backtesting.

One thing I found interesting was how changing the number of stocks in a portfolio affected its performance and risk.

I still want to improve the backtest by addressing survivorship bias and testing the strategy over different market conditions.
