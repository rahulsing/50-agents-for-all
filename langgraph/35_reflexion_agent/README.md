# Agent 35 - Reflexion Agent (LangGraph)

## What it does
Answers a research question, critiques its own answer (what is missing, what is superfluous), turns the critique into web searches, and rewrites the answer with the new evidence and a References line. Repeats for `--iterations` rounds.

## Concepts you learn
- **Reflexion vs Reflection:** Agent 08's critique only changes wording. Here the critique produces *search queries*, so the revision is based on new facts. Self-critique drives tool use.
- **Structured self-assessment, kept small:** the answer is plain text; a separate call returns a short `Critique` (`missing`, `superfluous`, `search_queries`). The first version asked for answer + critique in one big JSON object: the 7B model got stuck emitting whitespace for 20+ minutes (blocking Ollama for every other program), and with a length cap the JSON was cut off. Keep structured outputs small.
- **Grounded revision:** the revisor must cite the URLs it used.

## The graph
```
START -> draft (answer + critique + queries) -> search -> revise --(iterations left and new queries)--> search
                                                                \--(done)--> END
```

## Run
```
cd 50-agents-for-all
.venv-langgraph\Scripts\python.exe langgraph\35_reflexion_agent\main.py "What are the main benefits and risks of nuclear fusion energy?" --iterations 1
```
`--iterations` is clamped to 1-3. Empty question exits with code 1.

## Things to try
- Compare the first draft with the final answer: what did the searches add?
- Ask about something recent, where the draft is likely out of date.

## Known limits
- The critique tends to ask for 3-5 searches; only the first 3 are run.
- More iterations = more searches and a longer run.
