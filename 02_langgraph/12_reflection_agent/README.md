# Agent 12 - Reflection Agent (LangGraph)

## What it does
Give it a writing task. It writes a draft, a strict "editor" critiques it with 3 concrete improvements, and the writer rewrites. This repeats for `--rounds` drafts; every draft and critique is printed.

## Concepts you learn
- **Reflection pattern:** the same model plays two roles (writer and critic) with different prompts. Self-critique often improves output without any tools.
- **Custom state:** instead of a message list, the state is a `TypedDict` with `task`, `draft`, `critique`, `round`, `max_rounds`.
- **Loops in a graph:** `generate -> reflect -> generate` is a cycle; the conditional edge `should_continue` stops it after `max_rounds`.

## The graph
```
START -> generate --(round < max)--> reflect -> generate -> ... 
                  \--(done)--> END
```

## Run
```
cd 50-agents-for-all
.venv-langgraph\Scripts\python.exe 02_langgraph\12_reflection_agent\main.py "Write a 4-sentence LinkedIn post about learning Python as a beginner" --rounds 2
```
`--rounds` is clamped to 1-4. Empty task prints a message and exits with code 1.

## Things to try
- Compare `--rounds 1` (no critique) with `--rounds 3`.
- Change the critic's focus (for example "make it funnier" or "cut 30% of the words").
- Use a different model as the critic.

## Known limits
- Critiques can push the writer to invent specifics (in a test it added "web development" that the task never mentioned).
- More rounds is not always better; drafts can get longer and blander.
