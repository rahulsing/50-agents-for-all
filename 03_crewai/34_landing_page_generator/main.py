import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import common.crewai_env  # noqa: F401  (must come before crewai)

from crewai import Agent, Crew, Process, Task

from common.crewai_env import ollama_llm
from common.llm import DEFAULT_MODEL

OUT = Path(__file__).parent / "output"


def build_crew(idea: str) -> Crew:
    analyst = Agent(role="Product Analyst", goal="Clarify the idea's audience, problem and value",
                    backstory="You turn a vague idea into a crisp value proposition.",
                    llm=ollama_llm(DEFAULT_MODEL), allow_delegation=False, verbose=True)
    copywriter = Agent(role="Conversion Copywriter", goal="Write landing-page copy that converts",
                       backstory="You write short headlines, benefit-led sections and clear calls to action.",
                       llm=ollama_llm(DEFAULT_MODEL, temperature=0.5), allow_delegation=False, verbose=True)
    developer = Agent(role="Front-end Developer", goal="Build a clean, responsive single-file landing page",
                      backstory="You write semantic HTML with inline CSS, no external libraries.",
                      llm=ollama_llm(DEFAULT_MODEL, temperature=0.1), allow_delegation=False, verbose=True)

    t1 = Task(description=f"Idea: {idea}. Define: target audience, main problem, 3 key benefits, one-line "
                          "value proposition.", expected_output="Short bullets.", agent=analyst)
    t2 = Task(description="Write the landing-page copy: hero headline + subheadline, 3 benefit sections "
                          "(title + 2 sentences), 3 FAQs, and a call-to-action button text.",
              expected_output="Copy organised by section.", agent=copywriter, context=[t1])
    t3 = Task(description="Build ONE complete HTML5 file using the copy. Inline <style> only, mobile-friendly, "
                          "a hero section, benefit cards, FAQ, footer. Output only the HTML, starting with "
                          "<!DOCTYPE html>.",
              expected_output="A complete HTML document.", agent=developer, context=[t2])
    return Crew(agents=[analyst, copywriter, developer], tasks=[t1, t2, t3], process=Process.sequential)


def main() -> None:
    p = argparse.ArgumentParser(description="CrewAI landing page generator")
    p.add_argument("idea", nargs="?", default="")
    a = p.parse_args()
    if not a.idea.strip():
        print('Please describe the idea, e.g. main.py "an app that reminds you to water your plants"')
        sys.exit(1)
    raw = build_crew(a.idea.strip()).kickoff().raw
    match = re.search(r"<!DOCTYPE html>.*</html>", raw, re.S | re.I)  # strip any text around the HTML
    if not match:
        print("The developer did not return a full HTML page. Raw output:\n" + raw)
        sys.exit(2)
    OUT.mkdir(exist_ok=True)
    page = OUT / "index.html"
    page.write_text(match.group(0), encoding="utf-8")
    print(f"\nSaved {page} ({len(match.group(0))} characters). Open it in a browser.")


if __name__ == "__main__":
    main()
