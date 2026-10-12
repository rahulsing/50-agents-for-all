import argparse
import sys
from pathlib import Path
from typing import TypedDict

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph

from common.llm import DEFAULT_MODEL, OLLAMA_URL


class State(TypedDict):
    task: str
    draft: str
    critique: str
    round: int
    max_rounds: int


llm = ChatOllama(model=DEFAULT_MODEL, base_url=OLLAMA_URL, temperature=0.4)


def generate(state: State) -> dict:
    if state["critique"]:
        prompt = (f"Task: {state['task']}\n\nYour previous draft:\n{state['draft']}\n\n"
                  f"Reviewer feedback:\n{state['critique']}\n\nRewrite the draft applying every point. "
                  "Output only the new draft.")
    else:
        prompt = f"Task: {state['task']}\nWrite the best possible response. Output only the draft."
    draft = llm.invoke(prompt).content
    print(f"\n----- DRAFT {state['round'] + 1} -----\n{draft}")
    return {"draft": draft, "round": state["round"] + 1}


def reflect(state: State) -> dict:
    prompt = (f"You are a strict editor. Task: {state['task']}\n\nDraft:\n{state['draft']}\n\n"
              "Give 3 specific, actionable improvements as a numbered list (clarity, accuracy, structure, tone). "
              "Do not rewrite the draft.")
    critique = llm.invoke(prompt).content
    print(f"\n----- CRITIQUE {state['round']} -----\n{critique}")
    return {"critique": critique}


def should_continue(state: State) -> str:
    return "reflect" if state["round"] < state["max_rounds"] else END


def build_graph():
    g = StateGraph(State)
    g.add_node("generate", generate)
    g.add_node("reflect", reflect)
    g.add_edge(START, "generate")
    g.add_conditional_edges("generate", should_continue, ["reflect", END])
    g.add_edge("reflect", "generate")
    return g.compile()


def main() -> None:
    p = argparse.ArgumentParser(description="LangGraph reflection agent: draft, critique, rewrite")
    p.add_argument("task", nargs="?", default="")
    p.add_argument("--rounds", type=int, default=2, help="number of drafts (1-4)")
    a = p.parse_args()
    if not a.task.strip():
        print('Please provide a writing task, e.g. main.py "Write a LinkedIn post about learning Python"')
        sys.exit(1)
    rounds = max(1, min(a.rounds, 4))
    final = build_graph().invoke({"task": a.task.strip(), "draft": "", "critique": "", "round": 0,
                                  "max_rounds": rounds})
    print(f"\n===== FINAL (after {final['round']} drafts) =====\n{final['draft']}")


if __name__ == "__main__":
    main()
