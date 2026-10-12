# Agent 20 - Customer Support with human approval (LangGraph)

## What it does
A support chat for a fictional store (orders A100, A101, A102). Each message is classified (order status, refund, technical, other) and routed to a specialist. Order questions use a lookup tool. Refunds pause the whole graph until a human supervisor types y or n.

## Concepts you learn
- **Router + specialists:** a `classify` node with structured output picks the specialist node; each specialist has its own prompt and tools.
- **Human-in-the-loop with `interrupt()`:** inside the `request_refund` tool, `interrupt(...)` pauses the graph and returns control to your program. The program asks the supervisor and resumes with `graph.invoke(Command(resume="y"), config)`.
- **Checkpointer:** `InMemorySaver` + a `thread_id` is required for interrupts and also remembers the conversation across turns.
- **Policy in code:** refunds after 30 days are refused by the tool itself, before any human is asked.
- **Context-aware routing:** the router sees the last few messages, so "yes" after a refund question stays a refund.

## The graph
```
START -> classify --> order_status <-> order_status_tools
                  --> refund       <-> refund_tools (request_refund: interrupt -> human y/n)
                  --> technical
                  --> other
```

## Run
```
cd 50-agents-for-all
.venv-langgraph\Scripts\python.exe 02_langgraph\20_customer_support\main.py
```
Try: `Where is my order A101?`, then `I want a refund for order A100, the mouse is broken`, answer the `[SUPERVISOR]` prompt with `y`, then `exit`. Also try a refund for A102 (delivered 45 days ago).

## Things to try
- Answer `n` as the supervisor.
- Add a "cancel order" tool that also requires approval.

## Known limits
- Orders are a small dictionary, not a real database.
- In testing the refund specialist first asked the customer for photos instead of calling the tool; its prompt now tells it to act once it has an order id and a reason.
