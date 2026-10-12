# Agent 42 - Natural Language to SQL with a reviewer (AutoGen)

## What it does
Ask a question about the sample shop database. A `sql_writer` agent writes and runs SQLite SQL; a `reviewer` agent independently re-runs the SQL, compares the rows with what the writer reported, and only then gives the final answer and says APPROVED.

## Concepts you learn
- **Verification by a second agent, with its own tools:** in the first version the writer guessed column names (`order_id`) before reading the schema, every query failed, and it then *invented* a result ("5 orders, $1234.50"). The reviewer could only read the writer's text, so it approved the made-up numbers. The real answer was 37 orders worth 21,109.50. Now the reviewer has `run_sql` too and must re-run the query: a reviewer that can't check facts can't catch fabrication.
- **Check claims against real tool output, in code:** even with a tool, the reviewer once wrote the right SQL, then typed an imaginary result table instead of running it, and approved "12 orders, $10,299" (two numbers taken from different real rows). The custom `VerifiedApproval` termination condition now accepts APPROVED only if the numbers in the final answer appear together in one row that `run_sql` actually returned; otherwise the chat continues and the writer runs the corrected SQL.
- **Give context up front:** the schema is put in both system prompts by code, instead of hoping the model calls `get_schema` first.
- **Read-only by construction:** SQLite is opened with `mode=ro` and only SELECT/WITH queries are accepted.
- **RoundRobinGroupChat** with `VerifiedApproval() | MaxMessageTermination(9)`.

## The chat
```
question -> sql_writer (run_sql, fixes errors) -> reviewer (re-runs SQL, compares) -> APPROVED or "fix this" -> ...
```

## Run
```
cd 50-agents-for-all
.venv-autogen\Scripts\python.exe 04_autogen\42_nl_to_sql\main.py "How many orders did customers in Paris place, and what was their total value?"
```
Empty question exits with code 1. `shop.db` is created on first run (`common/sample_db.py`, same data as Agent 15).

## Things to try
- Check any answer yourself: open `shop.db` in a SQLite viewer and run the printed SQL.
- Ask a question with a trap ("orders in Paris last year" when all data is 2026).

## Known limits
- Two agents means more calls than Agent 15; it stops after 9 messages if they never agree.
- It can take several rounds: in a test the writer kept adding an unneeded `GROUP BY` (one row per customer) for 5 queries before the reviewer's correction gave the right single total.
- The guard checks numbers, not wording: an answer with no numbers is accepted as-is.
