# Agent 49 - CSV / SQL Query (LlamaIndex)

## What it does
Ask questions about a CSV file in plain English ("Which region had the highest total revenue?"). The CSV is loaded into an in-memory SQLite table, LlamaIndex turns your question into SQL, runs it, and answers from the result. The SQL is printed so you can check it.

## Concepts you learn
- **Text-to-SQL with `NLSQLTableQueryEngine`:** the engine shows the LLM the table schema, asks for SQL, executes it, then asks the LLM to phrase the answer from the returned rows.
- **CSV to a database:** a small loader guesses INTEGER / REAL / TEXT per column and creates the table with SQLAlchemy, so any CSV works.
- **Help the model with definitions:** the question gets "(revenue = units * unit_price)" appended, because the table has no revenue column.
- **Compare with Agents 15 and 42:** there the LLM drives a tool loop; here a fixed pipeline does one SQL query per question.

## The flow
```
CSV -> SQLite (in memory) -> question + schema -> LLM writes SQL -> run -> rows -> LLM answer
```

## Run
```
cd 50-agents-for-all
.venv-llamaindex\Scripts\python.exe 05_llamaindex\49_csv_sql_query\main.py "Which region had the highest total revenue?"
.venv-llamaindex\Scripts\python.exe 05_llamaindex\49_csv_sql_query\main.py "Average units per order by category" --csv path\to\other.csv
```
Empty question or missing CSV exits with code 1. With `--csv`, the table is still called `sales`.

## Things to try
- Ask for a monthly trend ("revenue per month") and check the SQL's date handling.
- Open the CSV in a spreadsheet and verify an answer by hand.

## Known limits
- One SQL query per question, no retry if the SQL is wrong.
- Only one table at a time.
