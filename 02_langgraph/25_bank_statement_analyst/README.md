# Agent 25 (extra) - Bank Statement Analyst (LangGraph)

## What it does
Reads a bank statement CSV (date, description, amount), categorises every transaction, computes monthly income/spend/savings and spending by category, flags unusual transactions (very large purchases, duplicate subscription charges, new large merchants), and writes a friendly report with a budget suggestion. A synthetic 3-month statement is generated on first run; it contains no real data.

## Concepts you learn
- **Pipeline graph:** a straight line of nodes (`categorise -> analyse -> write_report`) is still a useful LangGraph: each step is testable and the state shows what happened.
- **Rules first, LLM for the rest:** known merchants are categorised by a rules table; only unknown merchants (for example "CRYPTOFX GLOBAL LTD") go to the LLM with structured output.
- **Never let the LLM do the maths:** totals, medians, anomalies and even the top-3 ranking are computed in Python. In testing, the LLM picked the wrong top 3 and misread "2x" as "£2" until those were pre-computed. The LLM only explains the results.

## The graph
```
CSV -> categorise (rules + LLM) -> analyse (Python maths, anomaly rules) -> write_report (LLM) -> report
```

## Run
```
cd 50-agents-for-all
.venv-langgraph\Scripts\python.exe 02_langgraph\25_bank_statement_analyst\main.py
.venv-langgraph\Scripts\python.exe 02_langgraph\25_bank_statement_analyst\main.py path\to\your_statement.csv
```
A missing or empty file exits with code 1. Delete `sample_statement.csv` to regenerate it.

## Things to try
- Export a statement from your bank, rename the columns to `date,description,amount` (spending negative) and run it locally. Nothing leaves your machine.
- Add rules to `RULES` for your own merchants.
- Add an anomaly rule, for example "spending at night" or "foreign currency".

## Known limits
- Anomaly rules are simple heuristics and will miss or over-flag some cases.
- Currency is assumed to be GBP in the report. Educational tool only; not financial advice.
