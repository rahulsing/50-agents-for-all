import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console

from common.autogen_client import ollama_client
from common.llm import DEFAULT_MODEL
from common.tools import web_search as _web_search


def web_search(query: str) -> str:
    """Search the web. Returns titles, snippets and URLs."""
    return _web_search(query, 4)


SELECTOR_PROMPT = """You are the group chat manager. Choose who speaks next.
{roles}

Conversation so far:
{history}

Rules: planner speaks first; researcher gathers facts; writer writes the final answer once facts exist.
Select one of {participants}. Reply with the name only."""


async def run(task: str) -> None:
    client = ollama_client(DEFAULT_MODEL)
    planner = AssistantAgent("planner", model_client=client, description="Breaks the task into steps.",
                             system_message="Break the task into 2-3 research questions. Do not answer them.")
    researcher = AssistantAgent("researcher", model_client=client, tools=[web_search], reflect_on_tool_use=True,
                                description="Searches the web for facts.",
                                system_message="Answer the planner's research questions with web_search. "
                                               "Give facts with URLs.")
    writer = AssistantAgent("writer", model_client=client, description="Writes the final answer.",
                            system_message="Write the final answer for the user from the research (under 200 "
                                           "words, with sources). End your message with TERMINATE.")
    team = SelectorGroupChat(
        [planner, researcher, writer],
        model_client=client,  # the manager is an LLM that picks the next speaker each turn
        selector_prompt=SELECTOR_PROMPT,
        allow_repeated_speaker=False,
        termination_condition=TextMentionTermination("TERMINATE", sources=["writer"]) | MaxMessageTermination(12),
    )
    await Console(team.run_stream(task=task))
    await client.close()


def main() -> None:
    task = " ".join(sys.argv[1:]).strip()
    if not task:
        print('Please provide a task, e.g. main.py "Compare solar and wind power for a small farm"')
        sys.exit(1)
    asyncio.run(run(task))


if __name__ == "__main__":
    main()
