import operator
import sys
from pathlib import Path
from typing import Annotated, TypedDict

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ddgs import DDGS
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from common.llm import DEFAULT_MODEL, OLLAMA_URL

MAX_STEPS = 5
llm = ChatOllama(model=DEFAULT_MODEL, base_url=OLLAMA_URL, temperature=0)


@tool
def web_search(query: str) -> str:
    """Search the web and return short results with URLs."""
    return "\n".join(f"- {r['title']}: {r['body']} ({r['href']})" for r in DDGS().text(query, max_results=3))


class Plan(BaseModel):
    steps: list[str] = Field(description="2 to 4 short, concrete steps, in order")


class Replan(BaseModel):
    final_answer: str = Field(description="The final answer if the task is complete, otherwise empty")
    remaining_steps: list[str] = Field(description="Steps still needed, empty if the task is complete")


class State(TypedDict):
    task: str
    plan: list[str]
    past_steps: Annotated[list[tuple[str, str]], operator.add]
    answer: str


# The executor is itself a small tool-using agent (a subgraph) that handles one step at a time
executor = create_agent(llm, tools=[web_search],
                        system_prompt="Complete the given step. Use web_search for facts. Reply in under 80 words.")


def planner(state: State) -> dict:
    plan = llm.with_structured_output(Plan).invoke(f"Make a step-by-step plan for this task:\n{state['task']}")
    print("[plan]\n" + "\n".join(f"  {i}. {s}" for i, s in enumerate(plan.steps, 1)))
    return {"plan": plan.steps}


def execute(state: State) -> dict:
    step = state["plan"][0]
    done = "\n".join(f"- {s}: {r}" for s, r in state["past_steps"])
    out = executor.invoke({"messages": [("user", f"Task: {state['task']}\nDone so far:\n{done}\n\nNow do: {step}")]})
    result = out["messages"][-1].content
    print(f"\n[execute] {step}\n  -> {result[:300]}")
    return {"past_steps": [(step, result)]}


def replan(state: State) -> dict:
    done = "\n".join(f"- {s}: {r}" for s, r in state["past_steps"])
    if len(state["past_steps"]) >= MAX_STEPS:
        r = llm.invoke(f"Task: {state['task']}\nFindings:\n{done}\nWrite the final answer.").content
        return {"answer": r, "plan": []}
    r = llm.with_structured_output(Replan).invoke(
        f"Task: {state['task']}\nOriginal plan: {state['plan']}\nCompleted steps and results:\n{done}\n\n"
        "If the results are enough, give final_answer and no remaining_steps. Otherwise list remaining_steps.")
    if r.final_answer and not r.remaining_steps:
        return {"answer": r.final_answer, "plan": []}
    print(f"\n[replan] remaining: {r.remaining_steps}")
    return {"plan": r.remaining_steps or state["plan"][1:]}


def route(state: State) -> str:
    return END if state["answer"] or not state["plan"] else "execute"


def build_graph():
    g = StateGraph(State)
    g.add_node("planner", planner)
    g.add_node("execute", execute)
    g.add_node("replan", replan)
    g.add_edge(START, "planner")
    g.add_edge("planner", "execute")
    g.add_edge("execute", "replan")
    g.add_conditional_edges("replan", route, ["execute", END])
    return g.compile()


def main() -> None:
    task = " ".join(sys.argv[1:]).strip()
    if not task:
        print('Please provide a task, e.g. main.py "Who won the last FIFA World Cup and what is the captain\'s age?"')
        sys.exit(1)
    out = build_graph().invoke({"task": task, "plan": [], "past_steps": [], "answer": ""}, {"recursion_limit": 30})
    print(f"\n===== ANSWER =====\n{out['answer']}")


if __name__ == "__main__":
    main()
