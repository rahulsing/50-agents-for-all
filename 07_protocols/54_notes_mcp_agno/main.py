"""Agno agent that uses tools from a local MCP server (../notes_mcp_server.py)."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.mcp import MCPTools

from common.llm import DEFAULT_MODEL, OLLAMA_URL

SERVER = Path(__file__).resolve().parents[1] / "notes_mcp_server.py"


async def run(request: str) -> None:
    # MCPTools starts the server as a child process and talks to it over stdin/stdout (the "stdio" transport).
    # The agent never sees the server's code, only the tool names, descriptions and schemas it advertises.
    async with MCPTools(command=f'"{sys.executable}" "{SERVER}"', transport="stdio", timeout_seconds=30) as tools:
        agent = Agent(
            model=Ollama(id=DEFAULT_MODEL, host=OLLAMA_URL),
            tools=[tools],
            instructions=["You manage the user's notes with the notes tools. Confirm what you did in one sentence.",
                          "To answer questions about notes, search or list them first; never invent notes."],
            markdown=True,
            debug_mode=True,
        )
        await agent.aprint_response(request)


def main() -> None:
    request = " ".join(sys.argv[1:]).strip()
    if not request:
        print('Please give a request, e.g. main.py "Save a note called Groceries: milk, eggs, bread, tagged shopping"')
        sys.exit(1)
    asyncio.run(run(request))


if __name__ == "__main__":
    main()
