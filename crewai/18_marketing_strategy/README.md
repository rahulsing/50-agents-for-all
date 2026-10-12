# Agent 18 - Marketing Strategy Generator (CrewAI)

## What it does
Describe a product or business and a monthly budget. A market researcher searches the web for competitors, customers and trends; a strategist turns that into a structured plan: audience, positioning, 3 key messages, 3 channels (each with a first action) and 3 KPIs.

## Concepts you learn
- **Structured task output in CrewAI:** `Task(..., output_pydantic=MarketingStrategy)` validates the final answer into a Pydantic model. The code reads `result.pydantic.channels` instead of parsing text.
- **Nested models:** `channels: list[Channel]` shows that structured output can contain lists of objects.
- **Two-agent crew:** research (with a tool) feeds strategy (no tools) via `context=[research]`.
- **Shared helpers:** `common/crewai_env.py` disables telemetry, fixes the Windows console, and builds the Ollama `LLM`; `common/tools.py` has the search function.

## The crew
```
Market Researcher (web_search) --> Marketing Strategist --> MarketingStrategy (Pydantic)
```

## Run
```
cd 50-agents-for-all
.venv-crewai\Scripts\python.exe crewai\18_marketing_strategy\main.py "a vegan bakery in Manchester" --budget "800 GBP"
```
Empty product prints a message and exits with code 1. If validation fails it prints the raw text instead.

## Things to try
- Add a `budget_split: dict[str, int]` field to the model.
- Compare budgets of 200 vs 5000 and see if the channels change.

## Known limits
- KPI targets are guesses, not based on data.
- The plan uses web snippets only; it does not read full competitor pages.
