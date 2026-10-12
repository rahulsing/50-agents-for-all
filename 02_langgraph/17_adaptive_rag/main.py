import sys
from pathlib import Path
from typing import Literal, TypedDict

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ddgs import DDGS
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from common.llm import DEFAULT_MODEL, EMBED_MODEL, OLLAMA_URL

DOCS_DIR = Path(__file__).parent / "docs"
llm = ChatOllama(model=DEFAULT_MODEL, base_url=OLLAMA_URL, temperature=0)


class Route(BaseModel):
    datasource: Literal["handbook", "web_search", "direct"] = Field(
        description="handbook: anything about working here - leave, holidays, remote work, travel, meals, "
                    "expenses, allowances, passwords, security, laptops, equipment. "
                    "web_search: news, sports, prices, recent events, public facts that change. "
                    "direct: greetings, maths, stable general knowledge.")


class YesNo(BaseModel):
    score: Literal["yes", "no"]


class State(TypedDict):
    question: str
    route: str
    documents: list[str]
    answer: str


def build_store() -> InMemoryVectorStore:
    splitter = MarkdownHeaderTextSplitter([("#", "title"), ("##", "section")])
    chunks = [c for p in DOCS_DIR.glob("*.md") for c in splitter.split_text(p.read_text(encoding="utf-8"))]
    store = InMemoryVectorStore(OllamaEmbeddings(model=EMBED_MODEL, base_url=OLLAMA_URL))
    store.add_documents(chunks)
    return store


STORE = build_store()


def route_question(state: State) -> str:
    r = llm.with_structured_output(Route).invoke(
        "You route questions for an assistant at Acme Robotics. The user is an Acme employee, so questions about "
        f"work rules usually mean Acme's handbook.\nQuestion: {state['question']}")
    print(f"[router] -> {r.datasource}")
    return r.datasource


def retrieve(state: State) -> dict:
    docs = [d.page_content for d in STORE.similarity_search(state["question"], k=3)]
    grader = llm.with_structured_output(YesNo)
    kept = [d for d in docs if grader.invoke(
        f"Question: {state['question']}\nDocument: {d}\nIs the document relevant? yes or no.").score == "yes"]
    print(f"[handbook] {len(kept)} relevant chunks")
    return {"documents": kept, "route": "handbook"}


def after_retrieve(state: State) -> str:
    if state["documents"]:
        return "generate"
    print("[handbook] nothing relevant -> falling back to web search")
    return "web_search"


def web_search(state: State) -> dict:
    results = DDGS().text(state["question"], max_results=4)
    print(f"[web_search] {len(results)} results")
    return {"documents": [f"{r['title']}: {r['body']} ({r['href']})" for r in results], "route": "web_search"}


def generate(state: State) -> dict:
    context = "\n\n".join(state["documents"])
    answer = llm.invoke(f"Answer using only this context; cite URLs if present.\n\nContext:\n{context}\n\n"
                        f"Question: {state['question']}").content
    return {"answer": answer}


def direct(state: State) -> dict:
    return {"answer": llm.invoke(state["question"]).content, "route": "direct"}


def build_graph():
    g = StateGraph(State)
    for name, fn in [("retrieve", retrieve), ("web_search", web_search), ("generate", generate), ("direct", direct)]:
        g.add_node(name, fn)
    g.add_conditional_edges(START, route_question, {"handbook": "retrieve", "web_search": "web_search",
                                                    "direct": "direct"})
    g.add_conditional_edges("retrieve", after_retrieve, ["generate", "web_search"])
    g.add_edge("web_search", "generate")
    g.add_edge("generate", END)
    g.add_edge("direct", END)
    return g.compile()


def main() -> None:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        print("Please provide a question.")
        sys.exit(1)
    out = build_graph().invoke({"question": question, "route": "", "documents": [], "answer": ""})
    print(f"\n[source: {out['route']}]\n{out['answer']}")


if __name__ == "__main__":
    main()
