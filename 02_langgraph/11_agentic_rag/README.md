# Agent 11 - Agentic RAG (LangGraph)

## What it does
Answers questions about a company handbook (`docs/acme_handbook.md`). The agent decides whether it needs to search the handbook. Greetings get a direct reply; policy questions trigger a search first.

## Concepts you learn
- **RAG (retrieval-augmented generation):** instead of trusting the model's memory, fetch relevant text from your own documents and answer from that.
- **"Agentic" RAG:** retrieval is a *tool* the model chooses to call, not a fixed step. Classic RAG always retrieves; agentic RAG retrieves only when useful, and can search again if the first result is not enough.
- **LangGraph basics:** a graph of nodes (functions) joined by edges, sharing a state. Here the state is just the message list.
- **Embeddings:** each handbook section is turned into a vector; a question is turned into a vector too, and the closest sections are returned.

## The graph
```
START -> agent --(tool requested?)--> tools -> agent -> ... -> END
                 \--(no)--> END
```
- `agent` node: the model, with the search tool attached.
- `tools` node: runs `search_handbook` when the model asks.
- `tools_condition`: the router. Tool call in the reply goes to `tools`; otherwise the run ends.
- The `tools -> agent` edge is the loop: the model reads the results and can answer or search again.

## How the code works (`main.py`)
1. `MarkdownHeaderTextSplitter` cuts the handbook into one chunk per `##` section.
2. `OllamaEmbeddings` + `InMemoryVectorStore` embed and store the chunks (rebuilt at every start; fine for a small file).
3. `search_handbook` is a `@tool` returning the top 2 chunks with their section names.
4. The system prompt tells the model when to search, to answer only from results, and to cite the section.
5. `stream` prints each tool call, then the final answer.

## Run
```
cd 50-agents-for-all
.venv-langgraph\Scripts\python.exe 02_langgraph\11_agentic_rag\main.py "How many days of annual leave do I get?"
```
Add your own `.md` files to `docs/` to query them.

## Things to try
- Ask "Hi there" (no search) versus "What is the meal limit?" (search).
- Ask about something not in the handbook (pets) and check it admits it does not know.
- Change `k=2` to `k=1` or `k=4` in `search_handbook` and see how answers change.
- Ask a question spanning two sections ("remote work and equipment") and see if it searches twice.

## Known limits
- No relevance check on retrieved text. Agent 13 (Corrective RAG) adds that.
- Index is rebuilt on every run and held in memory only.
- Needs a model with good tool calling (`qwen2.5:7b-instruct` works).
