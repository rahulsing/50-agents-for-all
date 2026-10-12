import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, MessagesState, StateGraph

from common.llm import DEFAULT_MODEL, OLLAMA_URL
from common.tools import calculate, web_search as _web_search

MAX_TURNS = 6
llm = ChatOllama(model=DEFAULT_MODEL, base_url=OLLAMA_URL, temperature=0)


@tool
def web_search(query: str) -> str:
    """Search the web; returns short results with URLs."""
    return _web_search(query, 3)


@tool
def calculator(expression: str) -> str:
    """Evaluate an arithmetic expression such as '(70 - 55) / 55 * 100'."""
    return calculate(expression)


SHARED = ("You are working with a colleague on the user's request; you share one conversation. "
          "Do your part, then hand over. When the request is fully answered, start your reply with FINAL ANSWER.")
AGENTS = {
    "researcher": create_agent(llm, [web_search], system_prompt=SHARED + " You find facts and numbers on the web. "
                                                                         "Never calculate anything yourself: list "
                                                                         "the numbers and hand over to the analyst."),
    "analyst": create_agent(llm, [calculator], system_prompt=SHARED + " You compute every result with the "
                                                                       "calculator tool (never in your head) and "
                                                                       "explain the numbers. You cannot search. If "
                                                                       "a number is missing, ask the researcher."),
}


def make_node(name: str):
    def run(state: MessagesState) -> dict:
        reply = AGENTS[name].invoke({"messages": state["messages"]})["messages"][-1].content
        print(f"\n[{name}] {reply[:500]}")
        return {"messages": [HumanMessage(content=reply, name=name)]}
    return run


def router(state: MessagesState) -> str:
    last = state["messages"][-1]
    speakers = [getattr(m, "name", None) for m in state["messages"]]
    if len([s for s in speakers if s in AGENTS]) >= MAX_TURNS:
        return END
    # Only the analyst may finish: a researcher's "FINAL ANSWER" still goes to the analyst to verify the maths
    if "FINAL ANSWER" in last.content and last.name == "analyst":
        return END
    return "analyst" if last.name == "researcher" else "researcher"  # pass the baton to the other agent


def build_graph():
    g = StateGraph(MessagesState)
    for name in AGENTS:
        g.add_node(name, make_node(name))
        g.add_conditional_edges(name, router, ["researcher", "analyst", END])
    g.add_edge(START, "researcher")
    return g.compile()


def main() -> None:
    task = " ".join(sys.argv[1:]).strip()
    if not task:
        print('Please provide a task, e.g. main.py "Find the populations of Tokyo and Delhi and the percentage difference"')
        sys.exit(1)
    out = build_graph().invoke({"messages": [("user", task)]}, {"recursion_limit": 30})
    print(f"\n===== RESULT =====\n{out['messages'][-1].content}")


if __name__ == "__main__":
    main()
