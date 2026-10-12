# Agent 17 - Self-RAG (LangGraph)

## What it does
Answers handbook questions and then checks its own answer twice: is every claim supported by the retrieved text (no hallucination), and does it actually answer the question? If not, it regenerates or rewrites the search query and tries again (up to 2 retries).

## Concepts you learn
- **Self-RAG:** checks happen after generation, not just before. Agent 13 checks the inputs; this agent checks the output.
- **Two kinds of failure, two fixes:** not grounded -> regenerate; grounded but not useful -> rewrite the query and retrieve again.
- **Retry limits:** a `tries` counter in state stops endless loops.

## The graph
```
START -> retrieve -> grade_documents -> generate --(grounded and useful)--> END
                ^                         |--(not grounded)--> generate
                |                         \--(not useful)--> rewrite_query
                \------------------------------------------------/
```

## Run
```
cd 50-agents-for-all
.venv-langgraph\Scripts\python.exe langgraph\17_self_rag\main.py "Can I carry over unused leave?"
```
Empty question exits with code 1. The `[check]` lines show the self-assessment.

## Things to try
- Ask something the handbook doesn't cover and watch the rewrite loop, then the give-up message.
- Set `MAX_TRIES = 0` to disable retries.

## Known limits
- The same small model writes and judges, so it can approve its own mistakes.
- Each check is an extra LLM call (slower than plain RAG).
