import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import common.crewai_env  # noqa: F401  (must come before crewai)

from crewai import Agent, Crew, Process, Task

from common.crewai_env import ollama_llm
from common.llm import DEFAULT_MODEL

DEFAULT_STORY = Path(__file__).parent / "story.txt"


def build_crew(text: str) -> Crew:
    llm = ollama_llm(DEFAULT_MODEL, temperature=0.4)
    cleaner = Agent(role="Content Cleaner", goal="Remove spam, ads and off-topic lines",
                    backstory="You keep every real line of the conversation and drop the noise.",
                    llm=ollama_llm(DEFAULT_MODEL, temperature=0), allow_delegation=False, verbose=True)
    analyst = Agent(role="Story Analyst", goal="Find the characters, conflict and story beats",
                    backstory="You are a script editor who sees the drama in everyday conversations.",
                    llm=llm, allow_delegation=False, verbose=True)
    writer = Agent(role="Screenwriter", goal="Write a short, funny scene in proper screenplay format",
                   backstory="You write tight comedy with action lines and natural dialogue.",
                   llm=ollama_llm(DEFAULT_MODEL, temperature=0.7), allow_delegation=False, verbose=True)

    t1 = Task(description=f"Remove any spam or advertising from this text and return the rest unchanged:\n{text}",
              expected_output="The cleaned text.", agent=cleaner)
    t2 = Task(description="List the characters (one line each), the central conflict, and 4 story beats.",
              expected_output="Characters, conflict, beats.", agent=analyst, context=[t1])
    t3 = Task(description="Write a one-scene screenplay (about 300 words) in standard format: scene heading "
                          "(INT. OFFICE KITCHEN - MORNING), action lines, CHARACTER NAMES in caps above dialogue. "
                          "Keep the real events; add physical comedy.",
              expected_output="A screenplay scene.", agent=writer, context=[t1, t2])
    return Crew(agents=[cleaner, analyst, writer], tasks=[t1, t2, t3], process=Process.sequential)


def main() -> None:
    p = argparse.ArgumentParser(description="CrewAI screenplay writer: turns a conversation into a scene")
    p.add_argument("file", nargs="?", default=str(DEFAULT_STORY))
    a = p.parse_args()
    path = Path(a.file)
    text = path.read_text(encoding="utf-8").strip() if path.is_file() else ""
    if not text:
        print(f"File not found or empty: {path}")
        sys.exit(1)
    print("\n===== SCREENPLAY =====\n" + build_crew(text).kickoff().raw)


if __name__ == "__main__":
    main()
