# Protocols: how agents connect to the outside world

These extras take agents from the main 50 and connect them in three standard ways.

| Protocol | Connects | Folder |
|----------|----------|--------|
| **MCP** (Model Context Protocol) | an agent to **tools and data** served by a separate process | 54 (Agno client), 55 (LangGraph client), shared server `notes_mcp_server.py` |
| **A2A** (Agent2Agent) | an agent to **another agent**, discovered through its agent card | 56 (server), 57 (client) |
| **REST API** | **any program** to an agent over plain HTTP | 58 |

Rule of thumb: MCP = agent to tools, A2A = agent to agent, REST = anything to agent.

The folder is called `07_protocols/` (not `mcp/` or `a2a/`) so it cannot be confused with the installed `mcp` and `a2a` Python packages.
