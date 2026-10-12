import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.core.question_gen import LLMQuestionGenerator
from llama_index.core.tools import QueryEngineTool

from common.llamaindex_setup import use_ollama

DOCS = Path(__file__).parent / "docs"


def build_engine() -> SubQuestionQueryEngine:
    tools = []
    for path in sorted(DOCS.glob("*.md")):
        company = path.stem.split("_")[0]
        index = VectorStoreIndex.from_documents(SimpleDirectoryReader(input_files=[str(path)]).load_data())
        tools.append(QueryEngineTool.from_defaults(
            index.as_query_engine(similarity_top_k=3), name=company,
            description=f"2025 annual summary of {company.title()}: financials, operations, people, risks."))
    # The engine asks the LLM to split the question into one sub-question per tool, answers each,
    # then combines the sub-answers into one final answer. The default question generator needs an OpenAI
    # package, so we pass the prompt-based LLMQuestionGenerator, which works with any LLM (here Ollama).
    return SubQuestionQueryEngine.from_defaults(query_engine_tools=tools, use_async=False, verbose=True,
                                                question_gen=LLMQuestionGenerator.from_defaults())


def main() -> None:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        print('Please ask a question, e.g. main.py "Compare the revenue growth and margins of Northwind and Fresco"')
        sys.exit(1)
    use_ollama()
    response = build_engine().query(question)
    print(f"\n===== ANSWER =====\n{response}")


if __name__ == "__main__":
    main()
