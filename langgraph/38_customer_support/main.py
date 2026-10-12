import sys
import uuid
from pathlib import Path
from typing import Literal

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command, interrupt
from pydantic import BaseModel

from common.llm import DEFAULT_MODEL, OLLAMA_URL

llm = ChatOllama(model=DEFAULT_MODEL, base_url=OLLAMA_URL, temperature=0)

ORDERS = {  # sample data
    "A100": {"item": "Wireless mouse", "price": 25.0, "status": "delivered", "days_since_delivery": 5},
    "A101": {"item": "Standing desk", "price": 420.0, "status": "shipped", "eta_days": 2},
    "A102": {"item": "USB-C hub", "price": 39.0, "status": "delivered", "days_since_delivery": 45},
}


class State(MessagesState):
    intent: str


class Intent(BaseModel):
    intent: Literal["order_status", "refund", "technical", "other"]


@tool
def lookup_order(order_id: str) -> str:
    """Look up an order by id, e.g. A100."""
    o = ORDERS.get(order_id.upper())
    return str(o) if o else "No such order."


@tool
def request_refund(order_id: str, reason: str) -> str:
    """Issue a refund for an order. A human supervisor must approve it first."""
    o = ORDERS.get(order_id.upper())
    if not o:
        return "No such order."
    if o.get("days_since_delivery", 0) > 30:
        return "Refused: refunds are only possible within 30 days of delivery."
    # Pause the graph and wait for a human decision (resumed with Command(resume=...))
    decision = interrupt(f"Approve refund of {o['price']} USD for {order_id} ({o['item']})? Reason: {reason}")
    if str(decision).lower().startswith("y"):
        return f"Refund of {o['price']} USD approved and issued for {order_id}."
    return "The supervisor declined the refund."


TOOLS = {"order_status": [lookup_order], "refund": [lookup_order, request_refund]}
PROMPTS = {
    "order_status": "You handle order-status questions. Use lookup_order. Ask for the order id if missing.",
    "refund": "You handle refunds. As soon as you know the order id and any reason (e.g. 'broken'), call "
              "lookup_order and then request_refund in the same turn. Do not ask for photos or more details. "
              "Ask only for a missing order id. Then tell the customer the outcome.",
    "technical": "You give short, practical troubleshooting steps for gadgets the store sells.",
    "other": "You are a polite store assistant. Answer briefly or say a human will follow up.",
}


def classify(state: State) -> dict:
    recent = "\n".join(f"{m.type}: {m.content}" for m in state["messages"][-4:] if m.content)
    intent = llm.with_structured_output(Intent).invoke(
        f"Conversation so far:\n{recent}\n\nClassify the customer's LAST message. If it continues the previous "
        "topic (e.g. 'yes', or extra details), keep that topic.").intent
    print(f"[router] intent = {intent}")
    return {"intent": intent}


def make_specialist(intent: str):
    model = llm.bind_tools(TOOLS[intent]) if intent in TOOLS else llm

    def node(state: State) -> dict:
        return {"messages": [model.invoke([("system", PROMPTS[intent])] + state["messages"])]}
    return node


def build_graph():
    g = StateGraph(State)
    g.add_node("classify", classify)
    for intent in PROMPTS:
        g.add_node(intent, make_specialist(intent))
    for intent, tools in TOOLS.items():
        g.add_node(f"{intent}_tools", ToolNode(tools))
        g.add_conditional_edges(intent, tools_condition, {"tools": f"{intent}_tools", END: END})
        g.add_edge(f"{intent}_tools", intent)
    g.add_edge("technical", END)
    g.add_edge("other", END)
    g.add_edge(START, "classify")
    g.add_conditional_edges("classify", lambda s: s["intent"], list(PROMPTS))
    return g.compile(checkpointer=InMemorySaver())  # checkpointer = memory per thread + needed for interrupt


def main() -> None:
    graph = build_graph()
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    print("Customer support. Sample orders: A100, A101, A102. Type 'exit' to quit.")
    while True:
        try:
            text = input("\ncustomer> ").strip()
        except EOFError:
            break
        if text.lower() in {"exit", "quit"}:
            break
        if not text:
            continue
        result = graph.invoke({"messages": [("user", text)]}, config)
        while "__interrupt__" in result:  # human-in-the-loop: the graph is paused waiting for approval
            question = result["__interrupt__"][0].value
            try:
                answer = input(f"\n[SUPERVISOR] {question} (y/n) > ").strip()
            except EOFError:
                answer = "n"
            result = graph.invoke(Command(resume=answer), config)
        reply = next((m.content for m in reversed(result["messages"]) if isinstance(m, AIMessage) and m.content), "")
        print(f"\nagent> {reply}")


if __name__ == "__main__":
    main()
