import argparse
import sys
from pathlib import Path
from typing import TypedDict

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from common.llm import DEFAULT_MODEL, OLLAMA_URL
from common.tools import web_search

# num_predict caps every reply. The answer is written as plain text and only the short critique is structured:
# asking for answer + critique in ONE big JSON object first got the model stuck emitting whitespace for 20+
# minutes (blocking Ollama), and with a length cap the JSON was cut off before its last fields.
llm = ChatOllama(model=DEFAULT_MODEL, base_url=OLLAMA_URL, temperature=0, num_predict=1200)


class Critique(BaseModel):
    missing: str = Field(description="What important information is missing or unverified, one sentence")
    superfluous: str = Field(description="What is unnecessary or vague, one sentence")
    search_queries: list[str] = Field(description="1-3 short web searches that would fix what is missing")


def critique(question: str, answer: str) -> Critique:
    return llm.with_structured_output(Critique).invoke(
        f"Question: {question}\n\nAnswer:\n{answer}\n\nCritique this answer honestly and propose web searches.")


class State(TypedDict):
    question: str
    answer: str
    reflection: str
    queries: list[str]
    evidence: str
    iteration: int
    max_iterations: int


def first_draft(state: State) -> dict:
    answer = llm.invoke(f"Answer in about 120 words: {state['question']}").content
    c = critique(state["question"], answer)
    print(f"\n[draft]\n{answer}\n[self-critique] missing: {c.missing}\n[queries] {c.search_queries}")
    return {"answer": answer, "reflection": c.missing, "queries": c.search_queries[:3], "iteration": 0}


def run_searches(state: State) -> dict:
    evidence = "\n\n".join(f"Search: {q}\n{web_search(q, 3)}" for q in state["queries"])
    print(f"\n[search] ran {len(state['queries'])} queries")
    return {"evidence": evidence}


def revise(state: State) -> dict:
    answer = llm.invoke(
        f"Question: {state['question']}\n\nYour previous answer:\n{state['answer']}\n\n"
        f"Your critique: {state['reflection']}\n\nNew evidence from the web:\n{state['evidence']}\n\n"
        "Rewrite the answer (about 150 words) using the evidence. End with a 'References:' line listing the "
        "URLs you used.").content
    c = critique(state["question"], answer)
    n = state["iteration"] + 1
    print(f"\n[revision {n}]\n{answer}\n[self-critique] missing: {c.missing}")
    return {"answer": answer, "reflection": c.missing, "queries": c.search_queries[:3], "iteration": n}


def keep_going(state: State) -> str:
    return "search" if state["iteration"] < state["max_iterations"] and state["queries"] else END


def build_graph():
    g = StateGraph(State)
    g.add_node("draft", first_draft)
    g.add_node("search", run_searches)
    g.add_node("revise", revise)
    g.add_edge(START, "draft")
    g.add_edge("draft", "search")
    g.add_edge("search", "revise")
    g.add_conditional_edges("revise", keep_going, ["search", END])
    return g.compile()


def main() -> None:
    p = argparse.ArgumentParser(description="LangGraph Reflexion agent: answer, self-critique, search, revise")
    p.add_argument("question", nargs="?", default="")
    p.add_argument("--iterations", type=int, default=2)
    a = p.parse_args()
    if not a.question.strip():
        print("Please provide a question.")
        sys.exit(1)
    out = build_graph().invoke({"question": a.question.strip(), "answer": "", "reflection": "", "queries": [],
                                "evidence": "", "iteration": 0, "max_iterations": max(1, min(a.iterations, 3))})
    print(f"\n===== FINAL ANSWER =====\n{out['answer']}")


if __name__ == "__main__":
    main()
