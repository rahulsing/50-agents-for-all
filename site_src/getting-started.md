# Getting started

You need about 10 minutes, roughly 10 GB of free disk space, and ideally a GPU with 8 GB or more of memory (a CPU works, just slower).

## 1. Install Ollama and the models

Install Ollama from [ollama.com](https://ollama.com), then pull the models the agents use:

```bash
ollama pull qwen2.5:7b-instruct        # main model for all agents (good at tool calling)
ollama pull qwen3-embedding            # embeddings for the RAG agents
ollama pull qwen3-coder:30b            # optional: only agents 04 and 45 (code generation)
ollama pull qwen2.5:14b-instruct       # optional: a stronger model to compare with
```

Check it works:

```bash
ollama run qwen2.5:7b-instruct "Say hi"
```

!!! tip "Why qwen2.5 and not llama3.1?"
    In testing, `llama3.1:8b` printed its tool calls as plain text instead of actually calling the tools. `qwen2.5:7b-instruct` handles tool calling reliably at the same size.

## 2. Get the code

```bash
git clone https://github.com/rahulsing/50-agents-for-all.git
cd 50-agents-for-all
```

## 3. Create one Python environment per framework

The frameworks need different versions of the same libraries, so each gets its own virtual environment. Python **3.12** is recommended (some frameworks don't support 3.13+ yet). The examples use [uv](https://docs.astral.sh/uv/), which is fast; plain `python -m venv` + `pip` works too.

=== "Windows"

    ```powershell
    uv venv .venv-agno --python 3.12
    uv pip install --python .venv-agno\Scripts\python.exe -r agno\01_research_agent\requirements.txt
    ```

=== "macOS / Linux"

    ```bash
    uv venv .venv-agno --python 3.12
    uv pip install --python .venv-agno/bin/python -r agno/01_research_agent/requirements.txt
    ```

Repeat for the frameworks you want: `.venv-langgraph`, `.venv-crewai`, `.venv-autogen`, `.venv-llamaindex` (use any agent's `requirements.txt` in that framework's folder; all agents of a framework share one environment). The protocol extras use the Agno or LangGraph environment, as their pages say.

## 4. Run your first agent

=== "Windows"

    ```powershell
    .venv-agno\Scripts\python.exe agno\01_research_agent\main.py "What is retrieval augmented generation?"
    ```

=== "macOS / Linux"

    ```bash
    .venv-agno/bin/python agno/01_research_agent/main.py "What is retrieval augmented generation?"
    ```

You should see the tool calls (web searches) and then a 5-bullet answer with sources.

## 5. Change the model (optional)

All agents read their model names from one file, `common/llm.py`, and each can be overridden with an environment variable:

| Variable | Default | Used for |
|----------|---------|----------|
| `AGENT_MODEL` | `qwen2.5:7b-instruct` | almost every agent |
| `CODER_MODEL` | `qwen3-coder:30b` | code-writing agents (04, 45) |
| `EMBED_MODEL` | `qwen3-embedding:latest` | RAG agents |
| `OLLAMA_URL` | `http://localhost:11434` | where Ollama runs |

```bash
# example: try a bigger model with any agent
AGENT_MODEL=qwen2.5:14b-instruct python agno/12_finance_agent/main.py "Compare AAPL and MSFT"
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| An agent hangs for minutes | Run agents **one at a time**. Two programs asking the same model for different context sizes make Ollama reload it again and again. If Ollama stops answering, restart it. |
| `ModuleNotFoundError` | You are using the wrong environment: each framework has its own `.venv-<framework>`. |
| Web search returns nothing | Free search endpoints are rate-limited; wait a minute. The shared search tool already retries other backends. |
| Emoji errors on the Windows console | Already handled in the CrewAI agents; for others run `set PYTHONIOENCODING=utf-8`. |
| Very slow first run | Models load into memory on first use, and the RAG agents embed their documents once. |
