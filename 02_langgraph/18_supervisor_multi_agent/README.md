# Agent 18 - Supervisor Multi-Agent (LangGraph)

## What it does
A supervisor manages three workers: a researcher (web search), an analyst (calculator) and a writer. After each worker speaks, the supervisor decides who goes next, until the writer produces the final answer.

## Concepts you learn
- **Supervisor pattern:** one LLM call with structured output (`Next.next` = researcher / analyst / writer / FINISH) acts as a router. Workers never talk to each other directly; everything goes through the supervisor.
- **Workers are full agents:** each is built with `create_agent` and has its own tools and prompt.
- **Named messages:** worker replies are added as `HumanMessage(name=...)`, so the supervisor sees who said what.
- **Guardrails in code beat prompts:** the researcher kept doing the maths itself even when told not to, so the analyst was never used. A rule in `choose_next` now forces the analyst to check the numbers before the writer may run. When a model ignores instructions, enforce the workflow in code.
- **Safe calculator:** `common/tools.py` parses arithmetic with Python's `ast` instead of `eval`, so no code can be executed.

## Guardrails (LangChain middleware)
Search `main.py` for `GUARDRAIL` to find them. Every worker is built with `create_agent(..., middleware=[...])`:

| Middleware | Applied to | What it does |
|------------|------------|--------------|
| `PIIMiddleware("email", strategy="redact")` | all workers | Replaces emails in the input with `[REDACTED_EMAIL]` before the model sees them |
| `PIIMiddleware("credit_card", strategy="mask")` | all workers | Masks card numbers, keeping only the last 4 digits |
| `ModelCallLimitMiddleware(run_limit=5, exit_behavior="end")` | all workers | At most 5 model calls per worker turn: no endless loops |
| `ToolCallLimitMiddleware(tool_name="web_search", run_limit=2)` | researcher | At most 2 searches per turn; after that the model is told the limit is reached |
| `ToolCallLimitMiddleware(tool_name="calculator", run_limit=4)` | analyst | At most 4 calculations per turn |

`report_guardrails()` prints a `[guardrail]` line whenever PII was hidden or a limit was hit. Other strategies: `"block"` (raise an error), `"hash"`; `apply_to_output=True` also cleans the model's replies.

**Lesson from testing:** `PIIMiddleware` only cleans the *last* user message. In this graph each worker's reply is added as a new message, so only the first worker got the cleaned text; the analyst, the writer and the supervisor still saw the original email and card number. The fix is a `guard_input` node at the start of the graph that runs the same middleware's `before_model` hook once on the incoming message. The cleaned message replaces the original, so nobody downstream ever sees the raw PII. Middleware protects the agent it wraps; protect the whole graph at its entry.

There is also a hand-written workflow guardrail in `choose_next`: the writer can't run until the analyst has checked the numbers (see below).

## The graph
```
START -> guard_input (PII) -> supervisor --> researcher --+
            ^       --> analyst    --+--> supervisor ... --> writer -> FINISH
            +------------------------+
```
`MAX_HOPS = 6` caps the work.

## Run
```
cd 50-agents-for-all
.venv-langgraph\Scripts\python.exe 02_langgraph\18_supervisor_multi_agent\main.py "What is the population of Canada, and what is 2 percent of it?"
```
Empty task exits with code 1. Lines starting with `[supervisor]` show each routing decision and why.

## Things to try
- Ask a task with no maths and watch the analyst say "no calculation needed".
- Add a fourth worker (for example a translator).
- Compare with Agent 23 (no supervisor: agents pass the baton directly) and Agent 21 (supervisors of supervisors).

## Known limits
- Every routing decision is an extra LLM call.
- The guardrail sends the analyst even when there is nothing to calculate.
