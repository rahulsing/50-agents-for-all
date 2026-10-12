import sys
from pathlib import Path
from typing import Literal

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware, PIIMiddleware, ToolCallLimitMiddleware
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, MessagesState, StateGraph
from pydantic import BaseModel

from common.llm import DEFAULT_MODEL, OLLAMA_URL
from common.tools import calculate, web_search as _web_search

MAX_HOPS = 6
llm = ChatOllama(model=DEFAULT_MODEL, base_url=OLLAMA_URL, temperature=0)


@tool
def web_search(query: str) -> str:
    """Search the web; returns short results with URLs."""
    return _web_search(query, 3)


@tool
def calculator(expression: str) -> str:
    """Evaluate an arithmetic expression such as '(1200 * 0.15) / 3'."""
    return calculate(expression)


# ----- GUARDRAILS ---------------------------------------------------------------------------------------
# LangChain 1.x middleware wraps an agent's model and tool calls. Each worker gets its own guardrail stack.
def guardrails(*extra) -> list:
    return [
        PIIMiddleware("email", strategy="redact"),       # emails are replaced by [REDACTED_EMAIL] in the input
        PIIMiddleware("credit_card", strategy="mask"),   # card numbers become ****-****-****-1234
        ModelCallLimitMiddleware(run_limit=5, exit_behavior="end"),  # max 5 model calls per worker turn
        *extra,
    ]


# Each worker is its own small agent with its own tools and guardrails
WORKERS = {
    "researcher": create_agent(
        llm, [web_search],
        system_prompt="You find facts on the web and report them with URLs. Never do calculations; the analyst "
                      "does the maths.",
        # max 2 searches per turn; when the limit is hit the model is told so and must answer with what it has
        middleware=guardrails(ToolCallLimitMiddleware(tool_name="web_search", run_limit=2,
                                                      exit_behavior="continue"))),
    "analyst": create_agent(
        llm, [calculator],
        system_prompt="You check and do every calculation with the calculator tool. Show the expression and "
                      "result. If no calculation is needed, say so in one line.",
        middleware=guardrails(ToolCallLimitMiddleware(tool_name="calculator", run_limit=4,
                                                      exit_behavior="continue"))),
    "writer": create_agent(
        llm, [], system_prompt="You write the final answer for the user from the team's notes. Be clear and concise.",
        middleware=guardrails()),
}


INPUT_PII = [PIIMiddleware("email", strategy="redact"), PIIMiddleware("credit_card", strategy="mask")]


def guard_input(state: MessagesState) -> dict:
    """Graph-level guardrail: clean the user's message ONCE, before the supervisor or any worker sees it.

    PIIMiddleware inside an agent only cleans the LAST user message. Here worker replies are added as new
    messages, so without this node the analyst, the writer and the supervisor still saw the original
    email and card number (found in testing). Reusing the middleware's before_model hook keeps one set of rules,
    and the cleaned message keeps its id, so it replaces the original in the graph state."""
    messages = state["messages"]
    for mw in INPUT_PII:
        update = mw.before_model({"messages": messages}, None)
        if update:
            messages = update["messages"]
    if messages[-1].content != state["messages"][-1].content:
        print(f"  [guardrail] input: PII hidden for the whole team -> {messages[-1].content[:120]!r}")
    return {"messages": messages}


def report_guardrails(name: str, messages: list) -> None:
    """Print what the middleware did during one worker turn, so the guardrails are visible."""
    for m in messages:
        text = str(m.content)
        if m.type == "human" and ("[REDACTED" in text or "****" in text):
            print(f"  [guardrail] {name}: PII hidden before the model saw it -> {text[:120]!r}")
        if m.type == "tool" and "limit" in text.lower():
            print(f"  [guardrail] {name}: tool-call limit reached -> {text[:120]!r}")
# --------------------------------------------------------------------------------------------------------


class Next(BaseModel):
    next: Literal["researcher", "analyst", "writer", "FINISH"]
    reason: str


def supervisor(state: MessagesState) -> dict:
    return {}


def choose_next(state: MessagesState) -> str:
    hops = sum(1 for m in state["messages"] if getattr(m, "name", None) in WORKERS)
    last = state["messages"][-1]
    if getattr(last, "name", None) == "writer" or hops >= MAX_HOPS:
        return "FINISH"
    history = "\n".join(f"{getattr(m, 'name', None) or m.type}: {m.content[:400]}" for m in state["messages"])
    d = llm.with_structured_output(Next).invoke(
        "You are a supervisor managing workers: researcher (web facts), analyst (maths), writer (final answer).\n"
        "Pick the next worker. Use researcher for missing facts, analyst for calculations, "
        "and writer once the facts and numbers are ready.\n\nConversation so far:\n" + history)
    spoken = {getattr(m, "name", None) for m in state["messages"]}
    if d.next in ("writer", "FINISH") and "researcher" in spoken and "analyst" not in spoken:
        # Guardrail in code: numbers must be checked by the analyst (with the calculator) before writing
        print(f"[supervisor] wanted {d.next}, but the analyst has not verified the numbers -> analyst")
        return "analyst"
    print(f"[supervisor] -> {d.next} ({d.reason})")
    return d.next


def make_worker(name: str):
    def run(state: MessagesState) -> dict:
        out = WORKERS[name].invoke({"messages": state["messages"]})
        report_guardrails(name, out["messages"])
        content = out["messages"][-1].content
        print(f"\n[{name}] {content[:400]}")
        return {"messages": [HumanMessage(content=content, name=name)]}
    return run


def build_graph():
    g = StateGraph(MessagesState)
    g.add_node("guard_input", guard_input)  # GUARDRAIL: runs first
    g.add_node("supervisor", supervisor)
    for name in WORKERS:
        g.add_node(name, make_worker(name))
        g.add_edge(name, "supervisor")
    g.add_edge(START, "guard_input")
    g.add_edge("guard_input", "supervisor")
    g.add_conditional_edges("supervisor", choose_next, {**{n: n for n in WORKERS}, "FINISH": END})
    return g.compile()


def main() -> None:
    task = " ".join(sys.argv[1:]).strip()
    if not task:
        print('Please provide a task, e.g. main.py "What is the population of Canada and what is 2 percent of it?"')
        sys.exit(1)
    out = build_graph().invoke({"messages": [("user", task)]}, {"recursion_limit": 40})
    print(f"\n===== FINAL =====\n{out['messages'][-1].content}")


if __name__ == "__main__":
    main()
