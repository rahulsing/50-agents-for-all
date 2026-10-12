import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import common.crewai_env  # noqa: F401  (must come before crewai)

from crewai import Agent, Crew, Process, Task
from crewai.tools import tool

from common.crewai_env import ollama_llm
from common.llm import DEFAULT_MODEL
from common.tools import web_search as _web_search


@tool("web_search")
def web_search(query: str) -> str:
    """Search the web; returns titles, snippets and URLs."""
    return _web_search(query, 4)


def build_crew(company: str, objective: str, attendees: str) -> Crew:
    llm = ollama_llm(DEFAULT_MODEL)
    researcher = Agent(role="Company Researcher", goal=f"Brief the team on {company}",
                       backstory="You find recent, relevant facts and cite sources.",
                       tools=[web_search], llm=llm, allow_delegation=False, verbose=True)
    industry = Agent(role="Industry Analyst", goal=f"Explain the industry context around {company}",
                     backstory="You spot trends, competitors and pressures that matter in a meeting.",
                     tools=[web_search], llm=llm, allow_delegation=False, verbose=True)
    strategist = Agent(role="Meeting Strategist", goal="Prepare talking points and smart questions",
                       backstory="You turn research into a plan that helps reach the meeting objective.",
                       llm=llm, allow_delegation=False, verbose=True)
    writer = Agent(role="Briefing Writer", goal="Produce a one-page briefing",
                   backstory="You write tight, skimmable briefings for busy people.",
                   llm=llm, allow_delegation=False, verbose=True)

    t1 = Task(description=f"Research {company}: what it does, size, recent news (last 6 months), and anything "
                          f"about these attendees: {attendees}. Use web_search. Cite URLs.",
              expected_output="Bullets with sources.", agent=researcher)
    t2 = Task(description=f"Describe {company}'s industry: 3 trends, 3 competitors, 2 challenges.",
              expected_output="Short bullets.", agent=industry)
    t3 = Task(description=f"Meeting objective: {objective}. Write 4 talking points, 5 questions to ask, and 3 "
                          "likely objections with answers.",
              expected_output="Talking points, questions and objections.", agent=strategist, context=[t1, t2])
    t4 = Task(description="Combine everything into a one-page briefing: Objective, Company snapshot, Attendees, "
                          "Industry context, Talking points, Questions, Objections, Sources.",
              expected_output="A markdown briefing under 500 words.", agent=writer, context=[t1, t2, t3])
    return Crew(agents=[researcher, industry, strategist, writer], tasks=[t1, t2, t3, t4],
                process=Process.sequential)


def main() -> None:
    p = argparse.ArgumentParser(description="CrewAI meeting preparation")
    p.add_argument("company", nargs="?", default="")
    p.add_argument("--objective", default="explore a partnership")
    p.add_argument("--attendees", default="unknown")
    a = p.parse_args()
    if not a.company.strip():
        print('Please provide a company, e.g. main.py "Duolingo" --objective "sell our analytics tool"')
        sys.exit(1)
    print(build_crew(a.company.strip(), a.objective, a.attendees).kickoff().raw)


if __name__ == "__main__":
    main()
