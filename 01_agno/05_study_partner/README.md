# Agent 05 - Study Partner (Agno)

## What it does
An interactive tutor for any topic. Ask questions, type `quiz me` for a multiple-choice question, answer it, and it keeps your score. Sessions are saved, so you can stop and continue later.

## Concepts you learn
- **Session memory:** `db=SqliteDb(...)` stores every turn in `study_sessions.db`. `add_history_to_context=True` sends the last 8 turns with each new message, so the agent remembers the quiz it just asked.
- **Sessions by id:** `--session math` and `--session history` are separate conversations; reusing a name continues it, even after restarting the program.
- **A chat loop:** the program reads lines with `input()` until you type `exit`.

## The flow
```
you> message -> load session history from SQLite -> model (history + message) -> reply -> save turn
```

## Run
```
cd 50-agents-for-all
.venv-agno\Scripts\python.exe 01_agno\05_study_partner\main.py "Python decorators" --session py
```
Then type `What is a decorator?`, `quiz me`, `B`, `exit`. Missing topic prints a message and exits with code 1.

## Things to try
- Exit, run the same command again, and ask "What was my score?".
- Set `num_history_runs=1` and see the quiz break (it forgets the question).
- Open `study_sessions.db` with any SQLite viewer to see what is stored.

## Known limits
- The "score" is tracked by the model in conversation, not by code, so it can miscount.
- Delete `study_sessions.db` to reset everything.
