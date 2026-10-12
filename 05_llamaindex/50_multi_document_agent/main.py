import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from llama_index.core import Settings, SimpleDirectoryReader, SummaryIndex, VectorStoreIndex
from llama_index.core.agent.workflow import FunctionAgent, ToolCall
from llama_index.core.tools import QueryEngineTool

from common.llamaindex_setup import use_ollama

DOCS = Path(__file__).parent / "docs"


def build_tools() -> list[QueryEngineTool]:
    """Two tools per document: one for specific facts (vector search), one for overviews (summary)."""
    tools = []
    for path in sorted(DOCS.glob("*.md")):
        city = path.stem
        docs = SimpleDirectoryReader(input_files=[str(path)]).load_data()
        tools.append(QueryEngineTool.from_defaults(
            VectorStoreIndex.from_documents(docs).as_query_engine(similarity_top_k=2),
            name=f"{city}_facts",
            description=f"Specific facts about {city.replace('_', ' ').title()}: prices, transport, food, sights."))
        tools.append(QueryEngineTool.from_defaults(
            SummaryIndex.from_documents(docs).as_query_engine(response_mode="tree_summarize"),
            name=f"{city}_summary",
            description=f"A general overview of {city.replace('_', ' ').title()} for broad questions."))
    return tools


async def run(question: str) -> None:
    agent = FunctionAgent(
        tools=build_tools(), llm=Settings.llm,
        system_prompt="You answer travel questions using the city tools only. Use the *_facts tools for "
                      "specific details and *_summary tools for overviews. For comparisons, query each city. "
                      "Say which tools you used.")
    handler = agent.run(question)
    async for event in handler.stream_events():
        if isinstance(event, ToolCall):
            print(f"[tool call] {event.tool_name}({event.tool_kwargs})")
    print(f"\n{await handler}")


def main() -> None:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        print('Please ask a question, e.g. main.py "Compare public transport costs in Lisbon and Kyoto"')
        sys.exit(1)
    use_ollama()
    asyncio.run(run(question))


if __name__ == "__main__":
    main()
