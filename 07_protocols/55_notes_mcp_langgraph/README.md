# Agent 55 (extra) - Notes agent over MCP (LangGraph client)

## What it does
The same notes assistant as agent 54, built with LangGraph instead of Agno, using the **same** MCP server (`../notes_mcp_server.py`) and the same `notes.json`. Notes saved by one agent are visible to the other.

## Concepts you learn
- **MCP makes tools framework-independent:** no tool code was rewritten for LangGraph. `MultiServerMCPClient` (from `langchain-mcp-adapters`) connects to the server and converts its tools into LangChain tools.
- **Several servers at once:** `MultiServerMCPClient({...})` takes a dict, so one agent can combine tools from many MCP servers (notes, files, a database...).
- **Version independence:** this venv has `mcp` 1.x and the Agno venv has `mcp` 2.x; both talk to the same server because MCP is a protocol, not a library API.

## The flow
```
request -> create_agent (LangGraph) -> MCP tools -> notes_mcp_server.py -> notes.json
```

## Run
```
cd 50-agents-for-all
.venv-langgraph\Scripts\python.exe 07_protocols\55_notes_mcp_langgraph\main.py "What notes do I have about shopping?"
.venv-langgraph\Scripts\python.exe 07_protocols\55_notes_mcp_langgraph\main.py "Delete the groceries note"
```
Empty request exits with code 1. The first line printed is the list of tools discovered from the server.

## Things to try
- Add a second server to the dict (any public MCP server) and ask questions that need both.
- Compare the code size with agent 54.

## Known limits
- Each run starts a fresh server process; fine for demos, slower than a long-running server.
