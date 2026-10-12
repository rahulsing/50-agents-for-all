"""LangGraph agent that uses the SAME MCP server as agent 52, via langchain-mcp-adapters."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama

from common.llm import DEFAULT_MODEL, OLLAMA_URL

SERVER = Path(__file__).resolve().parents[1] / "notes_mcp_server.py"


async def run(request: str) -> None:
    client = MultiServerMCPClient({
        "notes": {"command": sys.executable, "args": [str(SERVER)], "transport": "stdio"},
    })
    tools = await client.get_tools()  # MCP tools converted into LangChain tools
    print(f"[mcp] tools from server: {[t.name for t in tools]}")
    agent = create_agent(ChatOllama(model=DEFAULT_MODEL, base_url=OLLAMA_URL, temperature=0), tools,
                         system_prompt="You manage the user's notes with the notes tools. Search or list notes "
                                       "before answering questions about them; never invent notes.")
    async for step in agent.astream({"messages": [("user", request)]}, stream_mode="values"):
        msg = step["messages"][-1]
        for call in getattr(msg, "tool_calls", None) or []:
            print(f"[tool call] {call['name']}({call['args']})")
    print(f"\n{msg.content}")


def main() -> None:
    request = " ".join(sys.argv[1:]).strip()
    if not request:
        print('Please give a request, e.g. main.py "What notes do I have about shopping?"')
        sys.exit(1)
    asyncio.run(run(request))


if __name__ == "__main__":
    main()
