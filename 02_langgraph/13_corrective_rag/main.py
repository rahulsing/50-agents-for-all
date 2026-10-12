import sys
from pathlib import Path
from typing import Literal, TypedDict

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ddgs import DDGS
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

from common.llm import DEFAULT_MODEL, EMBED_MODEL, OLLAMA_URL

DOCS_DIR = Path(__file__).parent / "docs"
llm = ChatOllama(model=DEFAULT_MODEL, base_url=OLLAMA_URL, temperature=0)


class Grade(BaseModel):
    relevant: Literal["yes", "no"]


class State(TypedDict):
    question: str
    documents: list[str]
    source: str
    answer: str


def build_store() -> InMemoryVectorStore:
    splitter = MarkdownHeaderTextSplitter([("#", "title"), ("##", "section")])
    chunks = [c for p in DOCS_DIR.glob("*.md") for c in splitter.split_text(p.read_text(encoding="utf-8"))]
    store = InMemoryVectorStore(OllamaEmbeddings(model=EMBED_MODEL, base_url=OLLAMA_URL))
    store.add_documents(chunks)
    return store


STORE = build_store()


def retrieve(state: State) -> dict:
    docs = STORE.similarity_search(state["question"], k=3)
    print(f"[retrieve] {len(docs)} chunks from the handbook")
    return {"documents": [d.page_content for d in docs], "source": "handbook"}


def grade_documents(state: State) -> dict:
    grader = llm.with_structured_output(Grade)
    kept = []
    for doc in state["documents"]:
        g = grader.invoke(f"Question: {state['question']}\n\nDocument:\n{doc}\n\n"
                          "Does the document contain information that helps answer the question? yes or no.")
        print(f"[grade] {g.relevant}: {doc[:60]!r}")
        if g.relevant == "yes":
            kept.append(doc)
    return {"documents": kept}


def decide(state: State) -> str:
    if state["documents"]:
        return "generate"
    print("[decide] no relevant handbook text -> web search")
    return "web_search"


def web_search(state: State) -> dict:
    query = llm.invoke(f"Rewrite this as a short web search query. Output only the query.\n{state['question']}").content
    print(f"[web_search] {query.strip()}")
    results = DDGS().text(query.strip().strip('"'), max_results=4)
    return {"documents": [f"{r['title']}: {r['body']} ({r['href']})" for r in results], "source": "web"}


def generate(state: State) -> dict:
    context = "\n\n".join(state["documents"])
    answer = llm.invoke(f"Answer the question using only this context. Be concise.\n\nContext:\n{context}\n\n"
                        f"Question: {state['question']}").content
    return {"answer": answer}


def build_graph():
    g = StateGraph(State)
    for name, fn in [("retrieve", retrieve), ("grade", grade_documents), ("web_search", web_search),
                     ("generate", generate)]:
        g.add_node(name, fn)
    g.add_edge(START, "retrieve")
    g.add_edge("retrieve", "grade")
    g.add_conditional_edges("grade", decide, ["generate", "web_search"])
    g.add_edge("web_search", "generate")
    g.add_edge("generate", END)
    return g.compile()


def main() -> None:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        print("Please provide a question.")
        sys.exit(1)
    out = build_graph().invoke({"question": question, "documents": [], "source": "", "answer": ""})
    print(f"\n[answered from: {out['source']}]\n{out['answer']}")


if __name__ == "__main__":
    main()
