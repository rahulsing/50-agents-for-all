import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from autogen_agentchat.agents import AssistantAgent, CodeExecutorAgent
from autogen_agentchat.base import TerminatedException, TerminationCondition
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage, StopMessage
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
from autogen_ext.models.ollama import OllamaChatCompletionClient

from common.llm import CODER_MODEL, OLLAMA_URL

WORKDIR = Path(__file__).parent / "workspace"

SYSTEM = """You are a Python programmer. Solve the task by writing ONE complete Python script
in a ```python code block. The script must print its result. You will see the output of running it.
If it failed, fix the code and send the full corrected script again.
Only after you have SEEN the execution output and it is correct, reply with a one-line summary and the word TERMINATE.
Never write TERMINATE in the same message as code."""


class DoneAfterExecution(TerminationCondition):
    """Stop when the coder says TERMINATE in a message that has no code block.

    Small models often write TERMINATE together with the code, before it has run.
    This ignores such messages so the executor still gets a turn.
    """

    def __init__(self) -> None:
        self._done = False

    @property
    def terminated(self) -> bool:
        return self._done

    async def __call__(self, messages):
        if self._done:
            raise TerminatedException("Termination condition has already been reached")
        for m in messages:
            text = m.to_text()
            if m.source == "coder" and "TERMINATE" in text and "```" not in text:
                self._done = True
                return StopMessage(content="Coder confirmed the result", source="DoneAfterExecution")
        return None

    async def reset(self) -> None:
        self._done = False


async def run(task: str, max_messages: int) -> None:
    WORKDIR.mkdir(exist_ok=True)
    model = OllamaChatCompletionClient(
        model=CODER_MODEL,
        host=OLLAMA_URL,
        temperature=0,
        options={"num_ctx": 16384},  # qwen3-coder defaults to a 262k context, far too big for most GPUs
        model_info={"vision": False, "function_calling": False, "json_output": False,
                    "family": "unknown", "structured_output": False},
    )
    coder = AssistantAgent("coder", model_client=model, system_message=SYSTEM)
    executor = CodeExecutorAgent(
        "executor", code_executor=LocalCommandLineCodeExecutor(work_dir=WORKDIR, timeout=60)
    )
    team = RoundRobinGroupChat(
        [coder, executor],
        termination_condition=DoneAfterExecution() | MaxMessageTermination(max_messages),
    )
    await Console(team.run_stream(task=task))
    await model.close()


def main() -> None:
    p = argparse.ArgumentParser(description="AutoGen coder + executor feedback loop")
    p.add_argument("task", nargs="?", default="")
    p.add_argument("--max-messages", type=int, default=10)
    a = p.parse_args()
    if not a.task.strip():
        print('Please provide a task, e.g. main.py "Print the first 10 primes"')
        sys.exit(1)
    asyncio.run(run(a.task.strip(), a.max_messages))


if __name__ == "__main__":
    main()
