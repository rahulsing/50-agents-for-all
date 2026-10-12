# Agent 14 - Stock Analysis (CrewAI)

## What it does
Give a ticker (for example NVDA). A financial data analyst pulls fundamentals and 6 months of prices from Yahoo Finance, a news researcher finds recent news, and a report writer produces a balanced report: summary, key figures, news, bull case, bear case and an overall view.

## Concepts you learn
- **Custom CrewAI tools:** `@tool("stock_fundamentals")` and `@tool("price_history")` wrap `yfinance` calls. The tool docstring is what the agent reads to decide when to use it.
- **Parallel-style inputs:** the report task takes `context=[t_numbers, t_news]`, combining two independent research tasks.
- **Separation of duties:** the agent with the numbers is told never to invent figures; the writer never touches tools.
- **Compare with Agent 12 (Agno):** one agent with a finance toolkit vs a team of three.

## The crew
```
Financial Data Analyst (fundamentals, price history) --+
Market News Researcher (web_search) --------------------+--> Investment Report Writer
```

## Run
```
cd 50-agents-for-all
.venv-crewai\Scripts\python.exe crewai\14_stock_analysis\main.py NVDA
```
An empty or malformed ticker prints a message and exits with code 1.

## Things to try
- Add a "technical analyst" agent using moving averages (see Agent 58 for code).
- Compare two runs a week apart.

## Known limits
- Yahoo Finance data may be delayed or missing fields (shown as `None`).
- The news section is often thin (headlines from search snippets, not article content), and the writer may follow the template too literally (it wrote "Neutral with one reason:").
- Educational use only, not financial advice.
