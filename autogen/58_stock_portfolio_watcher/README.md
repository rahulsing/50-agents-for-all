# Agent 58 (extra) - Stock Portfolio Watcher (AutoGen)

## What it does
Reads your holdings from `portfolio.csv` (ticker, shares, buy price), fetches current prices from Yahoo Finance, and reports value, profit/loss and weight per holding plus technical indicators (20/50-day moving averages, 14-day RSI, 1-month change). A risk reviewer then highlights concentration, overbought/oversold stocks and big losers.

## Concepts you learn
- **Numbers in tools, words in the model:** every number (P/L, weights, RSI) is computed in Python inside the tools; the analyst only explains them. This avoids the arithmetic mistakes small models make.
- **Many tool calls in one turn:** `max_tool_iterations=8` lets the analyst call `technical_indicators` once per ticker before answering.
- **Analyst + reviewer:** a second agent with a different focus (risk) adds a useful check.
- **Indicators from scratch:** moving averages and RSI with a few lines of pandas (`rolling`, `diff`, `clip`).

## The chat
```
portfolio_analyst: portfolio_snapshot -> technical_indicators (per ticker) -> report
risk_reviewer: 3 things to watch
```

## Run
```
cd 50-agents-for-all
.venv-autogen\Scripts\python.exe autogen\58_stock_portfolio_watcher\main.py
.venv-autogen\Scripts\python.exe autogen\58_stock_portfolio_watcher\main.py my_portfolio.csv
```
A missing portfolio file exits with code 1. Needs internet.

## Things to try
- Put your own holdings in a CSV (it stays on your machine).
- Add a dividend-yield tool.

## Known limits
- Prices may be delayed; indicators need about 50 trading days of history.
- Educational use only, not financial advice.
