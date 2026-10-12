# Agent 17 - Adaptive RAG (LangGraph)

## What it does
Routes each question to the best source before answering: the company handbook (with relevance grading), a web search, or a direct answer from the model. The output shows which route was used.

## Concepts you learn
- **Query routing:** a router LLM call with structured output (`Route.datasource`) decides the path *before* any retrieval. Cheap questions ("15 times 12") skip retrieval entirely.
- **Routing from START:** `add_conditional_edges(START, route_question, ...)` makes the first step a decision.
- **Descriptions are the router's only knowledge:** the first version sent "What is the meal allowance when travelling?" to "direct", because the router didn't know that topic lives in the handbook. Listing the handbook's topics in the field description and telling the router the user is an employee fixed it.
- **Fallback inside a route:** if the handbook has nothing relevant, the handbook path falls back to web search (as in Agent 13).

## The graph
```
START --router--> handbook: retrieve + grade --(relevant)--> generate -> END
                                             \--(none)--> web_search -> generate
              \-> web_search -> generate -> END
              \-> direct -> END
```

## Run
```
cd 50-agents-for-all
.venv-langgraph\Scripts\python.exe 02_langgraph\17_adaptive_rag\main.py "What is the meal allowance when travelling?"
.venv-langgraph\Scripts\python.exe 02_langgraph\17_adaptive_rag\main.py "What is 15 times 12?"
.venv-langgraph\Scripts\python.exe 02_langgraph\17_adaptive_rag\main.py "Who won the most recent Formula 1 drivers championship?"
```
Empty question exits with code 1.

## Things to try
- Ask ambiguous questions ("What's the password policy?" vs "What makes a strong password?") and see the routes.
- Add a fourth route (for example a calculator tool).

## Known limits
- Routing errors send a question to the wrong source; the router is only as good as its descriptions.
- When web results don't contain the answer, the model may fall back on outdated training data (seen in the F1 test).
