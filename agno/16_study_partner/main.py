import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.ollama import Ollama

from common.llm import DEFAULT_MODEL, OLLAMA_URL

DB_FILE = Path(__file__).parent / "study_sessions.db"


def build_agent(topic: str, session: str) -> Agent:
    return Agent(
        model=Ollama(id=DEFAULT_MODEL, host=OLLAMA_URL),
        db=SqliteDb(db_file=str(DB_FILE)),
        session_id=session,
        add_history_to_context=True,  # earlier turns of this session are sent with each new message
        num_history_runs=8,
        instructions=[
            f"You are a patient study partner for the topic: {topic}.",
            "Explain simply, with one short example. Keep answers under 150 words.",
            "When the user says 'quiz me', ask ONE multiple-choice question (A-D) and wait for the answer.",
            "When the user answers a quiz, say if it is right, explain why, and keep score across the session.",
        ],
        markdown=True,
    )


def main() -> None:
    p = argparse.ArgumentParser(description="Agno study partner with session memory")
    p.add_argument("topic", nargs="?", default="")
    p.add_argument("--session", default="default", help="same name = continue an earlier session")
    a = p.parse_args()
    if not a.topic.strip():
        print('Please provide a topic, e.g. main.py "Python decorators"')
        sys.exit(1)
    agent = build_agent(a.topic.strip(), a.session)
    print(f"Study partner for '{a.topic}'. Type 'quiz me', a question, or 'exit'.")
    while True:
        try:
            line = input("\nyou> ").strip()
        except EOFError:
            break
        if line.lower() in {"exit", "quit"}:
            break
        if line:
            agent.print_response(line)


if __name__ == "__main__":
    main()
