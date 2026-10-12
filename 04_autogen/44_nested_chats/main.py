import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.tools import TeamTool
from autogen_agentchat.ui import Console

from common.autogen_client import ollama_client
from common.llm import DEFAULT_MODEL


async def run(task: str) -> None:
    client = ollama_client(DEFAULT_MODEL)

    # Inner chat: two reviewers talk to each other about a draft
    critic = AssistantAgent("critic", model_client=client,
                            system_message="Critique the draft for clarity and persuasiveness. Give 3 bullet points.")
    fact_checker = AssistantAgent("fact_checker", model_client=client,
                                  system_message="Point out any claims that are vague, exaggerated or unverifiable. "
                                                 "Then summarise all feedback in 3 bullets and end with DONE.")
    review_team = RoundRobinGroupChat([critic, fact_checker], termination_condition=(
        TextMentionTermination("DONE", sources=["fact_checker"]) | MaxMessageTermination(3)))

    # The whole inner chat is exposed as ONE tool of the outer agent: a nested chat
    review_tool = TeamTool(team=review_team, name="review_draft",
                           description="Send a COMPLETE written draft to the review panel and get their combined "
                                       "feedback. The task argument must contain the full draft text.",
                           return_value_as_last_message=True)

    writer = AssistantAgent(
        "writer", model_client=client, tools=[review_tool], max_tool_iterations=2, reflect_on_tool_use=True,
        system_message="You write short marketing texts, and every text must be reviewed. Your FIRST action is "
                       "always a call to review_draft; do not write any message before it. Compose the draft in "
                       "your head and pass it as task = 'Review this draft: <your full draft>' (never the user's "
                       "request). After you get the feedback, apply it and output only the improved text after "
                       "the heading 'FINAL:'.")
    await Console(writer.run_stream(task=task))
    await client.close()


def main() -> None:
    task = " ".join(sys.argv[1:]).strip()
    if not task:
        print('Please provide a task, e.g. main.py "Write an 80-word product description for a smart water bottle"')
        sys.exit(1)
    asyncio.run(run(task))


if __name__ == "__main__":
    main()
