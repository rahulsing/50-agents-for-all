# Agent 22 - Code Assistant (LangGraph)

## What it does
Describe a small coding task. The assistant writes a Python solution as structured output (approach, imports, code), the graph actually runs it, and if the imports or the code fail, the error is fed back for a fix (up to 3 attempts).

## Concepts you learn
- **Structured code output:** `Code(prefix, imports, code)` separates parts so each can be checked; the import check catches missing libraries before running the full program.
- **Test-driven loop in a graph:** `generate -> check -> (error?) -> generate`. Real execution results, not the model's opinion, decide when to stop.
- **Running code safely-ish:** code runs in a separate `python` subprocess with a 30-second timeout and a temporary file.
- **Coder model:** uses `CODER_MODEL` (`qwen3-coder:30b`) from `common/llm.py`.

## The graph
```
START -> generate -> check --(passed or 3 attempts)--> END
                       \--(error)--> generate (with the error message)
```

## Run
```
cd 50-agents-for-all
.venv-langgraph\Scripts\python.exe 02_langgraph\22_code_assistant\main.py "A function that returns the n-th Fibonacci number using memoization, with a demo for n=30"
```
Empty task exits with code 1. The final block says WORKING or STILL FAILING.

## Things to try
- Ask for something needing a library you don't have (for example `requests`) and watch the import check fail and the fix.
- Compare with Agent 38 (AutoGen): there two agents talk; here a graph checks.

## Known limits
- Model-written code runs on your machine (in a subprocess). Keep tasks simple and read the code.
- "Passed" only means it ran without errors, not that the output is correct.
- The 30B model is slow to load the first time.
