# Agent 52 (extra) - Notes agent over MCP (Agno client)

## What it does
An Agno agent manages your notes ("save a note...", "what notes do I have about shopping?"). The note tools are not in the agent's code: they live in a separate MCP server, `../notes_mcp_server.py`, which stores notes in `../notes.json`.

## Concepts you learn
- **MCP (Model Context Protocol):** a standard way to serve tools to any AI client. The server advertises tools (name, description, input schema); clients discover and call them. The same server works with Agno, LangGraph (agent 53), Claude Code, Claude Desktop and others.
- **stdio transport:** `MCPTools(command="python notes_mcp_server.py", transport="stdio")` starts the server as a child process and talks JSON-RPC over its stdin/stdout. No network port is opened.
- **Async context manager:** `async with MCPTools(...)` starts the server, and stops it when the block ends.
- **Writing a server:** `@server.tool()` on a plain function is all it takes (FastMCP in `mcp` 1.x, `MCPServer` in 2.x; the server file supports both).

## The flow
```
request -> Agno agent -> MCPTools --stdio--> notes_mcp_server.py (add_note, list_notes, search_notes, delete_note)
                                                   \-> notes.json
```

## Run
```
cd 50-agents-for-all
.venv-agno\Scripts\python.exe protocols\52_notes_mcp_agno\main.py "Save a note called Groceries: milk, eggs, bread, tagged shopping"
.venv-agno\Scripts\python.exe protocols\52_notes_mcp_agno\main.py "What notes do I have about shopping?"
```
Empty request exits with code 1.

## Things to try
- Run agent 53 (LangGraph) and see it read the notes saved here.
- Add a tool to the server (for example `update_note`) and watch both clients pick it up with no client changes.
- Register the server in Claude Code: `claude mcp add notes -- python C:\...\protocols\notes_mcp_server.py`.

## Known limits
- The server is a demo: no locking, so two clients writing at the same moment could overwrite each other.
- Agno 3.x's `MCPTools` needs the separate `fastmcp` package (`fastmcp>=4,<5`); without it the agent fails at startup with an ImportError.
