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


def build_crew(product: str, audience: str) -> Crew:
    llm = ollama_llm(DEFAULT_MODEL, temperature=0.6)
    trend_scout = Agent(role="Social Trend Scout", goal="Find current Instagram angles and hashtags for the product",
                        backstory="You follow social media trends daily.", tools=[web_search], llm=llm,
                        allow_delegation=False, verbose=True)
    copywriter = Agent(role="Instagram Copywriter", goal="Write scroll-stopping captions",
                       backstory="You write short, warm captions with a clear call to action.", llm=llm,
                       allow_delegation=False, verbose=True)
    art_director = Agent(role="Visual Art Director", goal="Describe the photo or image for each post",
                         backstory="You write precise image-generation prompts (subject, setting, light, style).",
                         llm=llm, allow_delegation=False, verbose=True)

    task = Task(description=f"Create 3 Instagram posts for: {product}. Audience: {audience}. For each post give: "
                            "the caption (max 60 words, 1-2 emojis), 5 hashtags, and an image prompt.",
                expected_output="3 posts, each with Caption, Hashtags and Image prompt.")
    # Hierarchical process: CrewAI adds a manager agent that plans, delegates to the members and checks their work
    return Crew(agents=[trend_scout, copywriter, art_director], tasks=[task], process=Process.hierarchical,
                manager_llm=ollama_llm(DEFAULT_MODEL, temperature=0.2), verbose=True)


def main() -> None:
    p = argparse.ArgumentParser(description="CrewAI Instagram post generator (hierarchical crew)")
    p.add_argument("product", nargs="?", default="")
    p.add_argument("--audience", default="young professionals")
    a = p.parse_args()
    if not a.product.strip():
        print('Please describe the product, e.g. main.py "reusable coffee cups made from bamboo"')
        sys.exit(1)
    print("\n===== POSTS =====\n" + build_crew(a.product.strip(), a.audience).kickoff().raw)


if __name__ == "__main__":
    main()
