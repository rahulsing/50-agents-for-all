# 58 AI Agents on Your Own Computer

Learn how AI agents work by reading and running **58 small, complete examples** on free local models with [Ollama](https://ollama.com): no API keys, no cloud costs.

**📖 Read it as a tutorial website: https://rahulsing.github.io/50-agents-for-all/**

- **50 core agents** in five frameworks: LangGraph (14), CrewAI (12), Agno (10), AutoGen (9), LlamaIndex (5)
- **8 extras:** the same agent with no framework (Anthropic SDK), MCP, A2A, a REST API, a bank-statement analyst and a stock-portfolio watcher
- **Guardrails** with each framework's built-in features (Agno, CrewAI, LangChain middleware) plus hand-written ones
- Every agent has a `README.md` explaining the concepts, flow, how to run it, things to try, and **honest known limits from real testing on a 7B model**

## Quick start

```bash
ollama pull qwen2.5:7b-instruct
git clone https://github.com/rahulsing/50-agents-for-all.git && cd 50-agents-for-all
uv venv .venv-agno --python 3.12
uv pip install --python .venv-agno/bin/python -r 01_agno/01_research_agent/requirements.txt   # Windows: .venv-agno\Scripts\python.exe
.venv-agno/bin/python 01_agno/01_research_agent/main.py "What is retrieval augmented generation?"
```

Full setup: [Getting started](https://rahulsing.github.io/50-agents-for-all/getting-started/).

## Repository layout

| Path | Contents |
|------|----------|
| `01_agno/` (01-10), `02_langgraph/` (11-25), `03_crewai/` (26-37), `04_autogen/` (38-47), `05_llamaindex/` (48-52) | One folder per agent: `main.py`, `README.md`, `requirements.txt`, sample data |
| `06_anthropic_sdk/` | Agent 53: the agent loop with no framework |
| `07_protocols/` | Agents 54-58: MCP, A2A and REST API |
| `common/` | Shared helpers: model names (`llm.py`), web search and calculator tools, per-framework setup |
| [`INDEX.md`](INDEX.md) | All agents with links, by framework and by industry, plus where to find the guardrails |
| `site_src/`, `scripts/build_docs.py` | Source of the tutorial website |

## Build the website yourself

```bash
pip install mkdocs-material
python scripts/build_docs.py     # generates docs/ and mkdocs.yml from the agent folders
mkdocs serve                     # preview at http://127.0.0.1:8000
mkdocs gh-deploy --force         # publish to GitHub Pages (gh-pages branch)
```

## Credits

Agent ideas come from the community list [500 AI Agents Projects](https://github.com/ashishpatel26/500-AI-Agents-Projects). All code here is original, written for local models. All sample data (companies, people, orders, contracts) is fictional. Nothing here is financial or legal advice.
