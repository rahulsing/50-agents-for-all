import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import common.crewai_env  # noqa: F401  (must come before crewai)

from crewai import Agent, Crew, Process, Task
from crewai.tools import tool
from pydantic import BaseModel, Field

from common.crewai_env import ollama_llm
from common.llm import DEFAULT_MODEL
from common.tools import web_search as _web_search


@tool("web_search")
def web_search(query: str) -> str:
    """Search the web; returns titles, snippets and URLs."""
    return _web_search(query, 4)


class Channel(BaseModel):
    name: str = Field(description="e.g. Instagram, SEO blog, email, local events")
    why: str
    first_action: str


class MarketingStrategy(BaseModel):
    target_audience: str
    positioning: str = Field(description="One sentence: why choose us over alternatives")
    key_messages: list[str] = Field(description="3 short messages")
    channels: list[Channel] = Field(description="3 channels")
    kpis: list[str] = Field(description="3 measurable KPIs with targets")


def build_crew(product: str, budget: str) -> Crew:
    llm = ollama_llm(DEFAULT_MODEL)
    researcher = Agent(role="Market Researcher", goal=f"Understand the market and competitors for {product}",
                       backstory="You find who buys this kind of product and what competitors do well.",
                       tools=[web_search], llm=llm, allow_delegation=False, verbose=True)
    strategist = Agent(role="Marketing Strategist", goal="Turn research into a focused, realistic plan",
                       backstory="You work with small budgets and prefer few channels done well.",
                       llm=llm, allow_delegation=False, verbose=True)

    research = Task(description=f"Research the market for: {product}. Find 3 competitors or alternatives, "
                                "the typical customer, and 3 trends. Use web_search.",
                    expected_output="Bullets: competitors, typical customer, trends.", agent=researcher)
    strategy = Task(description=f"Create a marketing strategy for {product} with a monthly budget of {budget}.",
                    expected_output="A marketing strategy.", agent=strategist, context=[research],
                    output_pydantic=MarketingStrategy)  # the result is validated into this Pydantic model
    return Crew(agents=[researcher, strategist], tasks=[research, strategy], process=Process.sequential)


def main() -> None:
    p = argparse.ArgumentParser(description="CrewAI marketing strategy with structured output")
    p.add_argument("product", nargs="?", default="")
    p.add_argument("--budget", default="1000 USD")
    a = p.parse_args()
    if not a.product.strip():
        print('Please describe the product, e.g. main.py "a vegan bakery in Manchester"')
        sys.exit(1)
    result = build_crew(a.product.strip(), a.budget).kickoff()
    s: MarketingStrategy | None = result.pydantic
    if s is None:
        print(result.raw)
        return
    print(f"\n===== STRATEGY: {a.product} =====\nAudience: {s.target_audience}\nPositioning: {s.positioning}\n")
    print("Key messages:\n" + "\n".join(f"- {m}" for m in s.key_messages))
    print("\nChannels:")
    for c in s.channels:
        print(f"- {c.name}: {c.why}\n    first action: {c.first_action}")
    print("\nKPIs:\n" + "\n".join(f"- {k}" for k in s.kpis))


if __name__ == "__main__":
    main()
