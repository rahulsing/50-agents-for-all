# Agent 51 (extra) - Research Agent with the Anthropic SDK

## What it does
Same job as Agent 01 (Agno): web search, then a 5-bullet answer with source URLs. This version uses the plain `anthropic` Python SDK and no agent framework, so you can see what frameworks do for you.

## Concepts you learn
- **The Anthropic SDK works with Ollama.** Ollama exposes an Anthropic-compatible Messages API, so you only change `base_url`:
  `Anthropic(base_url="http://localhost:11434", api_key="ollama")`. The key is ignored. Switching to Claude later means changing these two values and the model name.
- **The agent loop, by hand.** An agent is just a loop:
  1. Send messages and tool definitions to the model.
  2. If `stop_reason == "tool_use"`, run each requested tool.
  3. Send the results back as `tool_result` blocks.
  4. Repeat until the model answers with no tool request.
- **Tool schema:** tools are described with a name, a description and a JSON `input_schema`. Compare with Agno, where `DuckDuckGoTools()` hides all this.

## The loop
```
question -> model --(stop_reason = tool_use)--> run web_search -> tool_result -> model -> ... -> final text
```
`MAX_TURNS = 6` stops runaway loops.

## How the code works (`main.py`)
1. `TOOLS` declares one tool, `web_search`.
2. `web_search()` calls DuckDuckGo (`ddgs`), no API key.
3. `research()` runs the loop above, appending assistant and tool-result messages each turn.
4. Model comes from `common/llm.py` (`qwen2.5:7b-instruct`).

## Run
```
cd 50-agents-for-all
.venv-anthropic\Scripts\python.exe anthropic_sdk\51_research_agent\main.py "What is retrieval augmented generation?"
```
Needs a recent Ollama (tested on 0.34.2). Empty question prints a message and exits with code 1.

## Things to try
- Compare the code size with `agno/01_research_agent`. What did the framework save you?
- Add a second tool (for example a calculator) and watch the model choose between them.
- Set `AGENT_MODEL=llama3.1:8b` and see how it handles tool calls through this API.
- Lower `MAX_TURNS` to 1 and see the guard message.

## Known limits
- No memory between runs, no retries, no streaming.
- Anthropic-only features (prompt caching, batches) are not available through Ollama.
- Tool use quality depends on the local model.
