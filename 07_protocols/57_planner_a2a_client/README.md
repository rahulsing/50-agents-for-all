# Agent 57 (extra) - Planner agent as an A2A client (LangGraph)

## What it does
A LangGraph planner that does no research itself. It discovers the research agent (agent 56) from its agent card, sends it each research question over A2A, and writes the final answer from the replies. Two agents in two different frameworks (LangGraph and Agno) cooperate through the protocol.

## Concepts you learn
- **Discovery:** the client first downloads `/.well-known/agent-card.json` and prints the remote agent's name and skills.
- **Sending a task:** `create_client(SERVER)` resolves the card and picks a transport; `client.send_message(SendMessageRequest(message=new_text_message(...)))` returns a stream of responses; `get_stream_response_text` extracts the text.
- **Delegation as a graph node:** the `delegate` node is async and calls the remote agent; the rest of the graph doesn't know or care that the work happened elsewhere.

## The graph
```
START -> plan (2 questions) -> delegate (A2A calls to agent 56) -> write -> END
```

## Run
Terminal 1: start agent 56.
```
cd 50-agents-for-all
.venv-agno\Scripts\python.exe 07_protocols\56_research_a2a_server\server.py
```
Terminal 2:
```
cd 50-agents-for-all
.venv-langgraph\Scripts\python.exe 07_protocols\57_planner_a2a_client\main.py "Should I visit Iceland in winter or summer to see the northern lights?"
```
If the server isn't running it prints how to start it and exits with code 1. Empty goal exits with code 1.

## Things to try
- Run agent 56 on another computer on your network and change `SERVER`.
- Ask the questions in parallel with `asyncio.gather`.

## Known limits
- In testing the planner often returned an empty question list, so the code falls back to sending the whole goal as one question; without that fallback it silently answered from its own memory and never called the remote agent.
- The client uses a 300-second HTTP timeout because the remote agent searches and runs a local LLM; the default timeout failed.
- A new client per question (simple, slightly slower).
