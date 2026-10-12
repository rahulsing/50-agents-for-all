# Agent 08 - Movie Recommendation (Agno)

## What it does
Tell it what you like; it recommends 3 movies from a local list (`movies.csv`, 25 films). It remembers you between runs: say "I already watched X" next time and it uses everything you said before.

## Concepts you learn
- **Memory across program runs:** a fixed `session_id` plus `db=SqliteDb(...)` and `add_history_to_context=True` means each run loads the earlier conversation from `movie_memory.db`.
- **Per-user memory:** `--user alice` and `--user bob` get separate memories.
- **Forcing tool use:** the first version ignored the tool and recommended films from its own memory that are not in the list. Stronger instructions ("ALWAYS call search_movies", "recommend ONLY titles it returned") fixed that.

## The flow
```
message -> load past turns (SQLite) -> model -> search_movies(genre, runtime, rating) -> 3 picks -> save turn
```

## Run
```
cd 50-agents-for-all
.venv-agno\Scripts\python.exe 01_agno\08_movie_recommendation\main.py "I loved Inception and Arrival but I hate horror. Recommend 3 movies."
.venv-agno\Scripts\python.exe 01_agno\08_movie_recommendation\main.py "I already watched Interstellar. Give me 3 different ones."
.venv-agno\Scripts\python.exe 01_agno\08_movie_recommendation\main.py --forget
```
Empty message prints a message and exits with code 1.

## Things to try
- Use two `--user` names with opposite tastes.
- Add films to `movies.csv`.
- Ask "What do you know about my taste?" to see what it remembers.

## Known limits
- Memory is the raw chat history, so after many turns old details drop out (`num_history_runs=10`).
- A 7B model sometimes re-recommends a film you said you liked (in a test it suggested Inception again).
