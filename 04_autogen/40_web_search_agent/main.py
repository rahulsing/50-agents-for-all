import asyncio
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import httpx
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console

from common.autogen_client import ollama_client
from common.llm import DEFAULT_MODEL
from common.tools import web_search as _web_search


def web_search(query: str) -> str:
    """Search the web. Returns titles, snippets and URLs."""
    return _web_search(query, 5)


def read_page(url: str) -> str:
    """Download a web page and return its visible text (first 3000 characters)."""
    try:
        html = httpx.get(url, timeout=15, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"}).text
    except httpx.HTTPError as e:
        return f"Could not fetch page: {e}"
    html = re.sub(r"(?is)<(script|style|nav|footer|header).*?</\1>", " ", html)
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
    return text[:3000]


async def run(question: str) -> None:
    client = ollama_client(DEFAULT_MODEL)
    agent = AssistantAgent(
        "web_researcher",
        model_client=client,
        tools=[web_search, read_page],
        max_tool_iterations=4,  # allow search -> read page -> search again, then answer
        reflect_on_tool_use=True,
        system_message="Answer using the web. First web_search, then read_page on the 1-2 most relevant URLs. "
                       "Answer in under 150 words and list the URLs you used under 'Sources:'.",
    )
    await Console(agent.run_stream(task=question))
    await client.close()


def main() -> None:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        print("Please provide a question.")
        sys.exit(1)
    asyncio.run(run(question))


if __name__ == "__main__":
    main()
