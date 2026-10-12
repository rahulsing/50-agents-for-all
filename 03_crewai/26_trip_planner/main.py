import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
os.environ.setdefault("CREWAI_DISABLE_TELEMETRY", "true")
os.environ.setdefault("OTEL_SDK_DISABLED", "true")
for _s in (sys.stdout, sys.stderr):
    _s.reconfigure(encoding="utf-8", errors="replace")  # Windows console cannot print CrewAI's emoji

from crewai import LLM, Agent, Crew, Process, Task
from crewai.tools import tool
from ddgs import DDGS

from common.llm import DEFAULT_MODEL, OLLAMA_URL


@tool("web_search")
def web_search(query: str) -> str:
    """Search the web and return the top results (title, snippet, url)."""
    results = DDGS().text(query, max_results=4)
    return "\n".join(f"- {r['title']}: {r['body']} ({r['href']})" for r in results) or "No results."


def build_crew(city: str, days: int, interests: str) -> Crew:
    llm = LLM(model=f"ollama/{DEFAULT_MODEL}", base_url=OLLAMA_URL, temperature=0.3)

    researcher = Agent(
        role="Local City Researcher",
        goal=f"Find the best sights, food and practical tips in {city}",
        backstory="You know cities well and always check the web for current information.",
        tools=[web_search],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
    planner = Agent(
        role="Itinerary Planner",
        goal="Turn research into a realistic day-by-day plan",
        backstory="You group nearby places together and keep each day balanced.",
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
    budgeter = Agent(
        role="Travel Budget Advisor",
        goal="Estimate costs and give money-saving tips",
        backstory="You give simple, honest daily cost estimates in USD.",
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    research = Task(
        description=f"Search the web for {city}. Interests: {interests}. "
        "List 8 attractions or restaurants that match, with one line each, plus 3 practical tips.",
        expected_output="A bullet list of 8 places and 3 tips.",
        agent=researcher,
    )
    plan = Task(
        description=f"Using the research, write a {days}-day itinerary for {city}. "
        "Give morning, afternoon and evening for each day.",
        expected_output=f"A {days}-day itinerary in markdown.",
        agent=planner,
        context=[research],
    )
    budget = Task(
        description=f"Estimate the daily cost in USD (budget, mid-range) for this {days}-day {city} trip "
        "and give 3 ways to save money.",
        expected_output="A short cost table and 3 saving tips.",
        agent=budgeter,
        context=[plan],
    )
    return Crew(agents=[researcher, planner, budgeter], tasks=[research, plan, budget], process=Process.sequential)


def main() -> None:
    p = argparse.ArgumentParser(description="CrewAI trip planner")
    p.add_argument("city", nargs="?", default="")
    p.add_argument("--days", type=int, default=3)
    p.add_argument("--interests", default="food, history")
    a = p.parse_args()
    if not a.city.strip():
        print("Please provide a city, e.g. main.py Lisbon --days 3")
        sys.exit(1)
    if not 1 <= a.days <= 7:
        print("--days must be between 1 and 7")
        sys.exit(1)
    result = build_crew(a.city.strip(), a.days, a.interests).kickoff()
    for title, out in zip(("RESEARCH", "ITINERARY", "BUDGET"), result.tasks_output):
        print(f"\n===== {title} =====\n")
        print(out.raw)


if __name__ == "__main__":
    main()
