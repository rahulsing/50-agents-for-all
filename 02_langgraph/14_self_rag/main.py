import sys
from pathlib import Path
from typing import Literal, TypedDict

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

from common.llm import DEFAULT_MODEL, EMBED_MODEL, OLLAMA_URL

DOCS_DIR = Path(__file__).parent / "docs"
MAX_TRIES = 2
llm = ChatOllama(model=DEFAULT_MODEL, base_url=OLLAMA_URL, temperature=0)


class YesNo(BaseModel):
    score: Literal["yes", "no"]


class State(TypedDict):
    question: str
    search_query: str
    documents: list[str]
    answer: str
    tries: int


def build_store() -> InMemoryVectorStore:
    splitter = MarkdownHeaderTextSplitter([("#", "title"), ("##", "section")])
    chunks = [c for p in DOCS_DIR.glob("*.md") for c in splitter.split_text(p.read_text(encoding="utf-8"))]
    store = InMemoryVectorStore(OllamaEmbeddings(model=EMBED_MODEL, base_url=OLLAMA_URL))
    store.add_documents(chunks)
    return store


STORE = build_store()


def ask_yes_no(prompt: str) -> str:
    return llm.with_structured_output(YesNo).invoke(prompt).score


def retrieve(state: State) -> dict:
    docs = STORE.similarity_search(state["search_query"], k=3)
    print(f"[retrieve] query={state['search_query']!r}")
    return {"documents": [d.page_content for d in docs]}


def grade_documents(state: State) -> dict:
    kept = [d for d in state["documents"]
            if ask_yes_no(f"Question: {state['question']}\nDocument: {d}\nIs the document relevant? yes or no.") == "yes"]
    print(f"[grade_documents] kept {len(kept)} of {len(state['documents'])}")
    return {"documents": kept}


def generate(state: State) -> dict:
    context = "\n\n".join(state["documents"]) or "(no relevant documents)"
    answer = llm.invoke(f"Answer using only the context. If it is not there, say you don't know.\n\n"
                        f"Context:\n{context}\n\nQuestion: {state['question']}").content
    print(f"[generate] try {state['tries'] + 1}")
    return {"answer": answer, "tries": state["tries"] + 1}


def check_answer(state: State) -> str:
    """Self-critique: is the answer grounded in the documents, and does it answer the question?"""
    if state["tries"] > MAX_TRIES:
        print("[check] giving up after max tries")
        return "done"
    context = "\n\n".join(state["documents"])
    grounded = ask_yes_no(f"Facts:\n{context}\n\nAnswer: {state['answer']}\n"
                          "Is every claim in the answer supported by the facts? yes or no.")
    print(f"[check] grounded: {grounded}")
    if grounded == "no":
        return "regenerate"
    useful = ask_yes_no(f"Question: {state['question']}\nAnswer: {state['answer']}\n"
                        "Does the answer resolve the question? yes or no.")
    print(f"[check] answers the question: {useful}")
    return "done" if useful == "yes" else "rewrite"


def rewrite_query(state: State) -> dict:
    new = llm.invoke(f"Rewrite this question so it finds better matches in a company handbook. "
                     f"Output only the rewritten question.\n{state['question']}").content.strip()
    return {"search_query": new}


def build_graph():
    g = StateGraph(State)
    g.add_node("retrieve", retrieve)
    g.add_node("grade_documents", grade_documents)
    g.add_node("generate", generate)
    g.add_node("rewrite_query", rewrite_query)
    g.add_edge(START, "retrieve")
    g.add_edge("retrieve", "grade_documents")
    g.add_edge("grade_documents", "generate")
    g.add_conditional_edges("generate", check_answer,
                            {"done": END, "regenerate": "generate", "rewrite": "rewrite_query"})
    g.add_edge("rewrite_query", "retrieve")
    return g.compile()


def main() -> None:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        print("Please provide a question.")
        sys.exit(1)
    out = build_graph().invoke({"question": question, "search_query": question, "documents": [], "answer": "",
                                "tries": 0})
    print(f"\n{out['answer']}")


if __name__ == "__main__":
    main()
