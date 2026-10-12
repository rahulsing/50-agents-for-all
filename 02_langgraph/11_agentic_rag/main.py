import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from common.llm import DEFAULT_MODEL, EMBED_MODEL, OLLAMA_URL

DOCS_DIR = Path(__file__).parent / "docs"
SYSTEM = (
    "You answer questions about the company handbook. "
    "For any question about company policy, call search_handbook first, "
    "then answer only from what it returns and name the section you used. "
    "If the handbook does not cover it, say so. For greetings, answer directly without searching."
)


def build_store() -> InMemoryVectorStore:
    splitter = MarkdownHeaderTextSplitter([("#", "title"), ("##", "section")])
    chunks: list[Document] = []
    for path in sorted(DOCS_DIR.glob("*.md")):
        chunks += splitter.split_text(path.read_text(encoding="utf-8"))
    store = InMemoryVectorStore(OllamaEmbeddings(model=EMBED_MODEL, base_url=OLLAMA_URL))
    store.add_documents(chunks)
    return store


def build_graph():
    store = build_store()

    @tool
    def search_handbook(query: str) -> str:
        """Search the company handbook for policy information."""
        hits = store.similarity_search(query, k=2)
        return "\n\n".join(f"[{d.metadata.get('section', '?')}] {d.page_content}" for d in hits)

    llm = ChatOllama(model=DEFAULT_MODEL, base_url=OLLAMA_URL, temperature=0).bind_tools([search_handbook])

    def agent(state: MessagesState):
        return {"messages": [llm.invoke([("system", SYSTEM)] + state["messages"])]}

    g = StateGraph(MessagesState)
    g.add_node("agent", agent)
    g.add_node("tools", ToolNode([search_handbook]))
    g.add_edge(START, "agent")
    g.add_conditional_edges("agent", tools_condition)
    g.add_edge("tools", "agent")
    return g.compile()


def main() -> None:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        print("Please provide a question.")
        sys.exit(1)
    for step in build_graph().stream({"messages": [("user", question)]}, stream_mode="values"):
        msg = step["messages"][-1]
        for call in getattr(msg, "tool_calls", None) or []:
            print(f"[tool call] {call['name']}({call['args']})")
        if msg.type == "ai" and msg.content:
            final = msg.content
    print("\n" + final)


if __name__ == "__main__":
    main()
