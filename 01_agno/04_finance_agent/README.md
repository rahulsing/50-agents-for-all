# Agent 04 - Finance Agent (Agno)

## What it does
Ask about stocks in plain English. The agent fetches live market data from Yahoo Finance (price, company info, ratios, analyst views) and answers with a table and three observations.

## Concepts you learn
- **Toolkit options:** `YFinanceTools(enable_stock_price=True, ...)` switches on only the tools you need. Fewer tools means fewer wrong tool choices for a small model.
- **"Never invent numbers":** the instructions force the model to fetch data instead of using memory, which may be years old.
- **Parallel tool calls:** for "AAPL and MSFT" the model calls the same tool once per ticker.

## The flow
```
question -> model -> get_current_stock_price / get_key_financial_ratios (per ticker) -> table + observations
```

## Run
```
cd 50-agents-for-all
.venv-agno\Scripts\python.exe 01_agno\04_finance_agent\main.py "What is the current price and P/E ratio of AAPL and MSFT?"
```
Empty question prints a message and exits with code 1. Needs internet.

## Things to try
- Enable `enable_company_news=True` and ask "Any recent news on NVDA?".
- Compare with Agent 28 (CrewAI stock analysis crew), which splits this work across three agents.
- Run with the larger model: `set AGENT_MODEL=qwen2.5:14b-instruct`.

## Known limits
- The 7B model can misread its own table (in a test it said MSFT had a larger market cap while the table showed AAPL's was larger) and can skip a requested metric. Check numbers against the table.
- Yahoo Finance data can be delayed. Educational use only, not financial advice.
