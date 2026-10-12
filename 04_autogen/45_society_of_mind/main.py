import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from autogen_agentchat.agents import AssistantAgent, SocietyOfMindAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console

from common.autogen_client import ollama_client
from common.llm import DEFAULT_MODEL


async def run(task: str, language: str) -> None:
    client = ollama_client(DEFAULT_MODEL, temperature=0.3)

    # The "inner mind": a writer and an editor discuss until the editor approves
    writer = AssistantAgent("writer", model_client=client,
                            system_message="Write or revise the text. Keep it under 120 words.")
    editor = AssistantAgent("editor", model_client=client,
                            system_message="Give the writer 2 concrete improvements. When the latest draft is good, "
                                           "reply only APPROVE.")
    inner = RoundRobinGroupChat([writer, editor], termination_condition=(
        TextMentionTermination("APPROVE", sources=["editor"]) | MaxMessageTermination(5)))

    # From outside, the whole inner team looks like ONE agent that answers with a single final message
    society = SocietyOfMindAgent("author", team=inner, model_client=client,
                                 response_prompt="Output only the final approved text, with no commentary.")
    translator = AssistantAgent("translator", model_client=client,
                                system_message=f"Translate the author's text into {language}. Output only the "
                                               "translation.")
    outer = RoundRobinGroupChat([society, translator], termination_condition=MaxMessageTermination(3))
    await Console(outer.run_stream(task=task))
    await client.close()


def main() -> None:
    p = argparse.ArgumentParser(description="AutoGen Society of Mind: an inner team acting as one agent")
    p.add_argument("task", nargs="?", default="")
    p.add_argument("--language", default="Spanish")
    a = p.parse_args()
    if not a.task.strip():
        print('Please provide a task, e.g. main.py "Write a welcome message for new gym members" --language French')
        sys.exit(1)
    asyncio.run(run(a.task.strip(), a.language))


if __name__ == "__main__":
    main()
