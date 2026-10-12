# Agent 56 (extra) - Research Agent as an A2A server

## What it does
Exposes an Agno research agent (like agent 01) through the **A2A (Agent2Agent) protocol**, so other agents, in any framework or language, can discover it and send it tasks. Agent 57 is a client for it. It uses the shared `common/tools.py` web search, which retries other search backends; Agno's built-in DuckDuckGo tool crashed the request when the search returned no results.

## Concepts you learn
- **Agent card:** a public JSON "business card" at `/.well-known/agent-card.json` with the agent's name, description, skills, examples and endpoint. Other agents read it to decide whether and how to call this one.
- **AgentExecutor:** the bridge between the protocol and your agent. `execute()` reads the incoming message (`context.get_user_input()`), runs the Agno agent, and puts a reply message on the `event_queue`.
- **Request handler + routes:** `DefaultRequestHandler` (with an in-memory task store) handles the JSON-RPC methods; `create_agent_card_routes` and `create_jsonrpc_routes` turn it into a Starlette web app served by uvicorn.
- **MCP vs A2A:** MCP exposes *tools* (the caller does the thinking). A2A exposes an *agent* (the remote side does its own reasoning, may take time, and can manage long tasks).

## Run
```
cd 50-agents-for-all
.venv-agno\Scripts\python.exe 07_protocols\56_research_a2a_server\server.py
```
Then open http://localhost:9999/.well-known/agent-card.json in a browser, and run agent 57 in a second terminal. `--port` changes the port.

## Things to try
- Add a second skill to the card (for example "summarise a URL").
- Wrap a different agent from this repo (for example agent 06) in the same executor.

## Known limits
- Uses the `a2a-sdk` 1.x API (protobuf types, route helpers). Older A2A tutorials use `A2AStarletteApplication`, which no longer exists in 1.x.
- No streaming or push notifications; one reply message per request.
- No authentication: it listens on 127.0.0.1 only.
