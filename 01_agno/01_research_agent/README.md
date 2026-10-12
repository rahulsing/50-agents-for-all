# Agent 01 - Research Agent (Agno)

## What it does
You ask a question. The agent searches the web with DuckDuckGo, then answers in 5 bullets and lists the source URLs.

## Concepts you learn
- **Agent = model + tools + instructions.** This is the whole agent; there is no graph or crew.
- **Tool calling:** the model does not search by itself. It emits a request ("call web_search with query X"), the framework runs the tool, and the result goes back to the model, which then writes the answer.
- **Instructions steer format** (5 bullets, sources at the end) without any extra code.

## How the code works (`main.py`)
1. `Ollama(id=DEFAULT_MODEL, host=OLLAMA_URL)` connects Agno to your local Ollama.
2. `DuckDuckGoTools()` gives the agent two tools: `web_search` and `search_news`. No API key needed.
3. `instructions=[...]` is the system prompt, as a list of rules.
4. `debug_mode=True` prints each tool call so you can see the agent really searched.
5. `print_response(question)` runs the agent and prints the answer.

```
question -> model -> "call web_search" -> DuckDuckGo -> results -> model -> 5 bullets + sources
```

## Run
```
cd 50-agents-for-all
.venv-agno\Scripts\python.exe 01_agno\01_research_agent\main.py "What is retrieval augmented generation?"
```
Empty question prints a message and exits with code 1.

## Things to try
- Change `Answer in exactly 5 bullet points` to `3 bullets` and re-run.
- Remove `DuckDuckGoTools()` and ask about recent news. Notice the model now guesses from old training data.
- Set `AGENT_MODEL=llama3.1:8b` and watch it print tool calls as text instead of running them. Not every model supports tool calling well.

## Known limits
- Small models sometimes return page titles instead of URLs in Sources.
- Search quality depends on DuckDuckGo; results can vary between runs.
