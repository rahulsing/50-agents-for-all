# Agent 13 - Corrective RAG (LangGraph)

## What it does
Answers questions from the company handbook (`docs/acme_handbook.md`), but first grades every retrieved chunk for relevance. If nothing relevant is found, it rewrites the question as a web query and searches the web instead. The output says where the answer came from.

## Concepts you learn
- **CRAG (Corrective RAG):** plain RAG trusts whatever the retriever returns. CRAG adds a grader that throws away irrelevant chunks and a fallback when the knowledge base can't answer. This fixes the "known limit" of Agent 02.
- **LLM as a classifier:** `llm.with_structured_output(Grade)` forces a strict `yes`/`no` answer per chunk.
- **Branching:** the conditional edge `decide` chooses between `generate` and `web_search`.

## The graph
```
START -> retrieve -> grade --(relevant chunks)--> generate -> END
                          \--(none)--> web_search -> generate
```

## Run
```
cd 50-agents-for-all
.venv-langgraph\Scripts\python.exe langgraph\13_corrective_rag\main.py "How many days of annual leave do employees get?"
.venv-langgraph\Scripts\python.exe langgraph\13_corrective_rag\main.py "What is the capital of Australia?"
```
The first answers from the handbook; the second falls back to the web. Empty question exits with code 1.

## Things to try
- Ask a question half in the handbook ("What laptop do new hires get and what does it cost?").
- Change `k=3` in `retrieve` and see grading decisions change.

## Known limits
- One grading call per chunk makes it slower than Agent 02.
- The fallback replaces the handbook entirely; it does not mix both sources.
