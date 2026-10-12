# Agent 01 - Research Agent

- Framework: Agno 3.1.2   Pattern: single agent + search
- Model: qwen2.5:7b-instruct (llama3.1:8b printed tool calls as text instead of running them)   Venv: .venv-agno (Python 3.12)

## Goal
Answer a research question with a 5-bullet cited summary from web search.

## Run
```
.venv-agno\Scripts\python.exe 01_agno\01_research_agent\main.py "What is retrieval augmented generation?"
```

## Test cases
| # | Input | Pass condition |
|---|-------|----------------|
| 1 | "What is retrieval augmented generation?" | 5 bullets and at least 2 source URLs |
| 2 | "Latest Ollama release" | search tool call visible in the debug log |
| 3 | (empty) | prints "Please provide a question." and exits 1 |

## Test log
| Date | Case | Result | Notes |
|------|------|--------|-------|



## Status
In progress - awaiting your test and approval
