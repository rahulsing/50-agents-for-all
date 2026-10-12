import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.duckduckgo import DuckDuckGoTools

from common.llm import DEFAULT_MODEL, OLLAMA_URL


def build_agent() -> Agent:
    return Agent(
        model=Ollama(id=DEFAULT_MODEL, host=OLLAMA_URL),
        tools=[DuckDuckGoTools()],
        instructions=[
            "Search the web before answering.",
            "Answer in exactly 5 bullet points.",
            "End with a 'Sources:' list of the full https:// URLs you used, not titles.",
        ],
        markdown=True,
        debug_mode=True,  # logs tool calls so you can verify the search ran
    )


def main() -> None:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        print("Please provide a question.")
        sys.exit(1)
    build_agent().print_response(question)


if __name__ == "__main__":
    main()
