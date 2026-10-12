import sys
from pathlib import Path
from typing import Literal

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, MessagesState, StateGraph
from pydantic import BaseModel, create_model

from common.llm import DEFAULT_MODEL, OLLAMA_URL
from common.tools import web_search as _web_search

llm = ChatOllama(model=DEFAULT_MODEL, base_url=OLLAMA_URL, temperature=0)
MAX_HOPS_PER_TEAM = 3


@tool
def web_search(query: str) -> str:
    """Search the web; returns short results with URLs."""
    return _web_search(query, 3)


def make_supervisor(members: list[str], job: str, max_hops: int):
    """A supervisor is an LLM call that picks the next member (or FINISH) with structured output."""
    Choice: type[BaseModel] = create_model("Choice", next=(Literal[tuple(members + ["FINISH"])], ...))

    def choose(state: MessagesState) -> str:
        hops = sum(1 for m in state["messages"] if getattr(m, "name", None) in members)
        if hops >= max_hops:
            return "FINISH"
        history = "\n".join(f"{getattr(m, 'name', None) or m.type}: {m.content[:300]}" for m in state["messages"])
        d = llm.with_structured_output(Choice).invoke(
            f"You supervise: {', '.join(members)}. {job}\nPick who acts next, or FINISH when the work is done. "
            f"Do not pick the same member twice in a row unless needed.\n\nSo far:\n{history}")
        print(f"  [{job.split('.')[0]}] -> {d.next}")
        return d.next
    return choose


def make_team(workers: dict, job: str):
    """Build one team as its own compiled graph (a subgraph)."""
    def as_node(worker_name, agent):
        def run(state: MessagesState) -> dict:
            out = agent.invoke({"messages": state["messages"]})["messages"][-1].content
            print(f"    [{worker_name}] {out[:200]}")
            return {"messages": [HumanMessage(content=out, name=worker_name)]}
        return run

    g = StateGraph(MessagesState)
    g.add_node("supervisor", lambda s: {})
    for w, agent in workers.items():
        g.add_node(w, as_node(w, agent))
        g.add_edge(w, "supervisor")
    g.add_edge(START, "supervisor")
    g.add_conditional_edges("supervisor", make_supervisor(list(workers), job, MAX_HOPS_PER_TEAM),
                            {**{w: w for w in workers}, "FINISH": END})
    return g.compile()


research_team = make_team({
    "searcher": create_agent(llm, [web_search], system_prompt="Find facts on the web. List facts with URLs."),
    "fact_checker": create_agent(llm, [web_search], system_prompt="Check the facts found so far with one more "
                                                                  "search. Say which are confirmed."),
}, "Research team. Gather and verify facts for the request.")

writing_team = make_team({
    "writer": create_agent(llm, [], system_prompt="Write the requested piece from the research notes."),
    "editor": create_agent(llm, [], system_prompt="Edit the latest draft for clarity. Cut it to the length the "
                                                  "user asked for in the first message. Return only the full "
                                                  "improved text."),
}, "Writing team. Produce and polish the final text.")


def team_node(name: str, team):
    def run(state: MessagesState) -> dict:
        print(f"\n[top supervisor] -> {name}")
        out = team.invoke({"messages": state["messages"]}, {"recursion_limit": 30})
        return {"messages": [HumanMessage(content=out["messages"][-1].content, name=name)]}
    return run


def top_choice(state: MessagesState) -> str:
    done = [getattr(m, "name", None) for m in state["messages"]]
    if "writing_team" in done:
        return "FINISH"
    TopChoice = create_model("TopChoice", next=(Literal["research_team", "writing_team", "FINISH"], ...))
    history = "\n".join(f"{getattr(m, 'name', None) or m.type}: {m.content[:300]}" for m in state["messages"])
    return llm.with_structured_output(TopChoice).invoke(
        "You lead two teams: research_team (finds facts) and writing_team (writes the text). "
        f"Research comes before writing. Pick the next team or FINISH.\n\n{history}").next


def build_graph():
    g = StateGraph(MessagesState)
    g.add_node("top", lambda s: {})
    g.add_node("research_team", team_node("research_team", research_team))
    g.add_node("writing_team", team_node("writing_team", writing_team))
    g.add_edge(START, "top")
    g.add_edge("research_team", "top")
    g.add_edge("writing_team", "top")
    g.add_conditional_edges("top", top_choice, {"research_team": "research_team", "writing_team": "writing_team",
                                                "FINISH": END})
    return g.compile()


def main() -> None:
    task = " ".join(sys.argv[1:]).strip()
    if not task:
        print('Please provide a task, e.g. main.py "Write a short blog post about the James Webb telescope"')
        sys.exit(1)
    out = build_graph().invoke({"messages": [("user", task)]}, {"recursion_limit": 30})
    print(f"\n===== FINAL =====\n{out['messages'][-1].content}")


if __name__ == "__main__":
    main()
