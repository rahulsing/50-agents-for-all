import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from anthropic import Anthropic
from ddgs import DDGS

from common.llm import DEFAULT_MODEL, OLLAMA_URL

MAX_TURNS = 6

SYSTEM = (
    "Search the web before answering. Answer in exactly 5 bullet points. "
    "End with a 'Sources:' list of the full https:// URLs you used, not titles."
)

TOOLS = [
    {
        "name": "web_search",
        "description": "Search the web. Returns title, snippet and URL for the top results.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "The search query"}},
            "required": ["query"],
        },
    }
]


def web_search(query: str) -> str:
    results = DDGS().text(query, max_results=4)
    return "\n".join(f"- {r['title']}: {r['body']} ({r['href']})" for r in results) or "No results."


def research(question: str) -> str:
    # Same Anthropic SDK you would use for Claude; only base_url points to local Ollama.
    client = Anthropic(base_url=OLLAMA_URL, api_key="ollama")
    messages = [{"role": "user", "content": question}]

    for _ in range(MAX_TURNS):
        resp = client.messages.create(
            model=DEFAULT_MODEL, max_tokens=1024, system=SYSTEM, tools=TOOLS, messages=messages
        )
        messages.append({"role": "assistant", "content": resp.content})

        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content if b.type == "text")

        results = []
        for block in resp.content:
            if block.type == "tool_use":
                print(f"[tool call] {block.name}({block.input})")
                results.append(
                    {"type": "tool_result", "tool_use_id": block.id, "content": web_search(**block.input)}
                )
        messages.append({"role": "user", "content": results})

    return "Stopped: too many tool calls without a final answer."


def main() -> None:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        print("Please provide a question.")
        sys.exit(1)
    print("\n" + research(question))


if __name__ == "__main__":
    main()
