import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import common.crewai_env  # noqa: F401  (must come before crewai)

from crewai import Agent, Crew, Process, Task
from pydantic import BaseModel, Field

from common.crewai_env import ollama_llm
from common.llm import DEFAULT_MODEL

DATA = Path(__file__).parent / "data"


class Requirement(BaseModel):
    requirement: str = Field(description="One must-have from the job description, e.g. 'SQL'")
    met: bool
    evidence: str = Field(description="Exact words from the CV that prove it, or 'not in CV'")


class CandidateScore(BaseModel):
    name: str
    must_haves: list[Requirement] = Field(description="One entry for EVERY must-have in the job description")
    summary: str = Field(description="Two sentences")

    @property
    def score(self) -> int:
        """Computed in code, not by the model: the share of must-haves that are met."""
        return round(100 * sum(r.met for r in self.must_haves) / max(len(self.must_haves), 1))

    @property
    def missing(self) -> list[str]:
        return [r.requirement for r in self.must_haves if not r.met]


def build_crew(job: str, cvs: dict[str, str]) -> tuple[Crew, list[Task], Agent, Agent]:
    llm = ollama_llm(DEFAULT_MODEL, temperature=0)
    screener = Agent(role="CV Screener", goal="Score each candidate fairly against the must-have requirements",
                     backstory="You only use facts written in the CV and ignore names, gender and age.",
                     llm=llm, allow_delegation=False, verbose=True)
    interviewer = Agent(role="Interview Designer", goal="Prepare targeted interview questions",
                        backstory="You probe gaps and verify claimed skills with practical questions.",
                        llm=llm, allow_delegation=False, verbose=True)
    hr = Agent(role="HR Coordinator", goal="Give the hiring manager a clear shortlist",
               backstory="You write short, decision-ready summaries.", llm=llm, allow_delegation=False, verbose=True)

    # One screening task per CV: small models are more reliable with one document at a time
    screens = [Task(description=f"Job description:\n{job}\n\nCV:\n{cv}\n\nFor EACH must-have in the job "
                                "description, decide if the CV shows it and quote the evidence. A skill only "
                                "counts if the CV states it.",
                    expected_output="A requirement-by-requirement check.", agent=screener,
                    output_pydantic=CandidateScore)
               for cv in cvs.values()]
    return Crew(agents=[screener], tasks=screens, process=Process.sequential), screens, interviewer, hr


def report_crew(ranking: str, interviewer: Agent, hr: Agent) -> Crew:
    questions = Task(description=f"Screening results (scores computed from must-haves met):\n{ranking}\n\n"
                                 "Write 3 interview questions for each of the top 2 candidates that probe their "
                                 "missing or unproven skills.",
                     expected_output="Questions grouped by candidate.", agent=interviewer)
    shortlist = Task(description=f"Screening results:\n{ranking}\n\nWrite the hiring manager a shortlist in the "
                                 "same order (do not change scores), a recommendation of who to interview, and the "
                                 "questions.",
                     expected_output="A markdown shortlist.", agent=hr, context=[questions])
    return Crew(agents=[interviewer, hr], tasks=[questions, shortlist], process=Process.sequential)


def main() -> None:
    job_file, cv_dir = DATA / "job_description.txt", DATA / "candidates"
    cvs = {p.stem: p.read_text(encoding="utf-8") for p in sorted(cv_dir.glob("*.txt"))}
    if not job_file.exists() or not cvs:
        print(f"Need {job_file} and at least one CV in {cv_dir}")
        sys.exit(1)
    screen_crew, screens, interviewer, hr = build_crew(job_file.read_text(encoding="utf-8"), cvs)
    screen_crew.kickoff()
    scored = sorted((t.output.pydantic for t in screens if t.output and t.output.pydantic), key=lambda s: -s.score)
    ranking = "\n".join(f"{s.score:>3}  {s.name}: missing {s.missing or 'nothing'} - {s.summary}" for s in scored)
    print(f"\n===== SCORES (computed in code) =====\n{ranking}")
    for s in scored:
        for r in s.must_haves:
            print(f"   {s.name:<14} {'MET ' if r.met else 'MISS'} {r.requirement}: {r.evidence}")
    result = report_crew(ranking, interviewer, hr).kickoff()
    print(f"\n===== SHORTLIST =====\n{result.raw}")


if __name__ == "__main__":
    main()
