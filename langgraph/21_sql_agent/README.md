# Agent 21 - SQL Agent (LangGraph)

## What it does
Ask questions about a sample shop database in plain English ("Which city's customers spent the most?"). The agent explores the schema, writes SQL, runs it, fixes errors, and answers with the SQL it used.

## Concepts you learn
- **Tool-using agent loop** (same graph shape as Agent 02) with three database tools: `list_tables`, `describe_table`, `run_query`.
- **Explore before you query:** describing tables (columns + sample rows) first gives the model what it needs to write correct joins.
- **Safety by design:** the database is opened read-only (`mode=ro`) and `run_query` rejects anything that isn't `SELECT`. The agent cannot change data even if the model tries.
- **Self-correction:** SQL errors are returned to the model as text, so it can fix and retry.

## The graph
```
START -> agent --(tool call)--> tools -> agent -> ... -> answer + SQL
```
`shop.db` is created on first run by `common/sample_db.py` (15 customers, 10 products, 200 orders, fixed seed).

## Run
```
cd 50-agents-for-all
.venv-langgraph\Scripts\python.exe langgraph\21_sql_agent\main.py "Which city's customers spent the most money in total?"
.venv-langgraph\Scripts\python.exe langgraph\21_sql_agent\main.py "What are the 3 best selling products by quantity?"
```
Empty question exits with code 1.

## Things to try
- Ask "Delete all orders" and see the guard refuse.
- Ask something needing 3 joins ("Which product category is most popular in Berlin?").
- Compare with Agent 25 (AutoGen), where a second agent reviews the SQL.

## Known limits
- Answers may omit the numbers behind a ranking unless you ask for them.
- Only returns the first 20 rows.
