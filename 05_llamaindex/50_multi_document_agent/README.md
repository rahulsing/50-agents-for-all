# Agent 50 - Multi-Document Agent (LlamaIndex)

## What it does
Answers travel questions across three city guides (Lisbon, Kyoto, Cape Town; fictional sample data). For each city the agent has two tools: one for specific facts and one for overviews. It picks the right tools, queries several cities for comparisons, and says which tools it used.

## Concepts you learn
- **Two indexes per document:** a `VectorStoreIndex` (fast, finds specific passages) and a `SummaryIndex` with `tree_summarize` (reads the whole document, good for "what is X like?").
- **Query engines as tools:** `QueryEngineTool.from_defaults(engine, name, description)`. The description is what the agent uses to choose.
- **FunctionAgent (LlamaIndex agent workflows):** an async agent that calls tools via the model's function calling. `handler.stream_events()` lets you watch each `ToolCall`.
- **Scaling idea:** with many documents you would retrieve the right tools first (`tool_retriever`) instead of giving the agent all of them.

## The flow
```
question -> FunctionAgent -> lisbon_facts / kyoto_facts / cape_town_summary ... -> combined answer
```

## Run
```
cd 50-agents-for-all
.venv-llamaindex\Scripts\python.exe 05_llamaindex\50_multi_document_agent\main.py "Compare the cost of public transport passes in Lisbon and Kyoto"
.venv-llamaindex\Scripts\python.exe 05_llamaindex\50_multi_document_agent\main.py "Which city is best for a food lover, and why?"
```
Empty question exits with code 1. Add a city by dropping a `.md` file in `docs/`.

## Things to try
- Ask an overview question and check it uses a `*_summary` tool.
- Add a fourth city guide.

## Known limits
- Prices are in local currencies; in a test it reported "7 EUR" vs "700 JPY" without converting (see Agent 39 for a currency tool).
