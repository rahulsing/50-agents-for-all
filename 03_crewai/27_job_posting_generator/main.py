import argparse
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import common.crewai_env  # noqa: F401  (must come before crewai)

from crewai import Agent, Crew, Process, Task, TaskOutput
from crewai.tools import tool

from common.crewai_env import ollama_llm
from common.llm import DEFAULT_MODEL
from common.tools import web_search as _web_search

OUT = Path(__file__).parent / "output"

# ----- GUARDRAILS ---------------------------------------------------------------------------------------
# A CrewAI task guardrail validates the task's output BEFORE it is accepted. Returning (False, feedback) sends
# the feedback to the agent, which must redo the task (up to guardrail_max_retries times).
MAX_WORDS = 450
BIASED_TERMS = ["rockstar", "ninja", "guru", "young", "digital native", "he", "his", "him", "manpower",
                "salesman", "chairman", "native english speaker"]
REQUIRED_SECTIONS = ["Responsibilities", "Requirements"]
# Money that is PAY: an amount next to a pay word, or followed by "per year"/"a year"/"pa". The first version
# flagged ANY currency amount and rejected "customer deposits exceeding £25 billion" on every retry.
SALARY = re.compile(r"(salary|compensation|pay|wage)[^.\n]{0,40}[$£€]\s?\d"
                    r"|[$£€]\s?\d[\d,.]*\s?k?\s*(per (year|annum|hour)|a year|/\s?(year|yr)|p\.?a\b)", re.I)


def posting_rules(result: TaskOutput) -> tuple[bool, Any]:
    """Function guardrail: deterministic checks on the final posting (length, wording, structure, salary)."""
    text = result.raw
    problems = []
    words = len(text.split())
    if words > MAX_WORDS:
        # Small models can't count words, so the feedback says WHAT to cut, not just the number
        problems.append(f"it has {words} words, at least {words - MAX_WORDS + 30} too many: shorten 'About us' "
                        "to 2 sentences, keep at most 4 bullets per section, and delete the closing paragraph")
    found = [t for t in BIASED_TERMS if re.search(rf"\b{re.escape(t)}\b", text, re.I)]
    if found:
        problems.append(f"replace biased or gendered wording: {', '.join(found)}")
    missing = [s for s in REQUIRED_SECTIONS if s.lower() not in text.lower()]
    if missing:
        problems.append(f"add the missing sections: {', '.join(missing)}")
    if SALARY.search(text):
        problems.append("remove salary figures; no salary was provided")
    if problems:
        print(f"\n[guardrail] posting rejected -> retry: {'; '.join(problems)}\n")
        return False, "Fix these problems and return the full posting: " + "; ".join(problems)
    print(f"\n[guardrail] posting passed the rules ({words} words)\n")
    return True, result


# A plain-English guardrail: CrewAI turns this sentence into an LLM check (LLMGuardrail) using the agent's model.
FAIRNESS_RULE = ("The job posting must not contain requirements based on age, gender, nationality, religion or "
                 "family status, and must describe the requested role.")
# --------------------------------------------------------------------------------------------------------


@tool("web_search")
def web_search(query: str) -> str:
    """Search the web; returns titles, snippets and URLs."""
    return _web_search(query, 4)


def build_crew(company: str, role: str, notes: str) -> Crew:
    llm = ollama_llm(DEFAULT_MODEL)
    researcher = Agent(role="Company Researcher", goal=f"Understand {company}'s business and culture",
                       backstory="You research companies quickly and summarise what candidates care about.",
                       tools=[web_search], llm=llm, allow_delegation=False, verbose=True)
    writer = Agent(role="Job Description Writer", goal="Write clear, inclusive, attractive job postings",
                   backstory="You are an experienced recruiter who avoids jargon and biased wording.",
                   llm=llm, allow_delegation=False, verbose=True)
    reviewer = Agent(role="Hiring Content Reviewer", goal="Make postings accurate, concise and inclusive",
                     backstory="You check tone, gendered language, unrealistic requirements and length.",
                     llm=llm, allow_delegation=False, verbose=True)

    research = Task(description=f"Search for {company}. Summarise what it does, its products, and its culture "
                                "or values in 5 bullets.",
                    expected_output="5 bullets about the company.", agent=researcher)
    draft = Task(description=f"Write a job posting for a {role} at {company}. Notes from the hiring manager: "
                             f"{notes}. Sections: About us, The role, Responsibilities, Requirements, "
                             "Nice to have, Benefits.",
                 expected_output="A job posting in markdown.", agent=writer, context=[research])
    review = Task(description="Review and improve the posting: remove biased or gendered words, keep requirements "
                              "realistic (max 6), keep it under 400 words. Return the final posting only.",
                  expected_output="The final job posting in markdown.", agent=reviewer, context=[draft],
                  guardrails=[posting_rules, FAIRNESS_RULE],  # GUARDRAILS: code check, then LLM check
                  guardrail_max_retries=3,
                  output_file=str(OUT / "job_posting.md"))  # CrewAI writes the task result to this file
    return Crew(agents=[researcher, writer, reviewer], tasks=[research, draft, review], process=Process.sequential)


def main() -> None:
    p = argparse.ArgumentParser(description="CrewAI job posting generator")
    p.add_argument("company", nargs="?", default="")
    p.add_argument("--role", default="Junior Python Developer")
    p.add_argument("--notes", default="hybrid work, team of 6, Python and SQL")
    a = p.parse_args()
    if not a.company.strip():
        print('Please provide a company, e.g. main.py "Spotify" --role "Data Analyst"')
        sys.exit(1)
    OUT.mkdir(exist_ok=True)
    try:
        result = build_crew(a.company.strip(), a.role, a.notes).kickoff()
    except Exception as e:  # raised when the output still fails a guardrail after all retries
        print(f"\n[guardrail] The posting could not pass the guardrails: {e}")
        sys.exit(3)
    print(f"\n===== JOB POSTING (saved to {OUT / 'job_posting.md'}) =====\n{result.raw}")


if __name__ == "__main__":
    main()
