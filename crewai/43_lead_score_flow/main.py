import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import common.crewai_env  # noqa: F401  (must come before crewai)

from crewai import Agent
from crewai.flow.flow import Flow, listen, router, start
from pydantic import BaseModel, Field

from common.crewai_env import ollama_llm
from common.llm import DEFAULT_MODEL

HERE = Path(__file__).parent
PRODUCT = "ForecastIQ, a demand-forecasting SaaS for retailers and logistics companies (from 30 USD/seat/month)"


class LeadScore(BaseModel):
    budget: bool = Field(description="Has, or clearly can get, budget for a paid product")
    authority: bool = Field(description="Can this person make or strongly influence the decision?")
    need: bool = Field(description="Has a real business need the product solves")
    timing: bool = Field(description="Wants to buy within ~3 months")
    reason: str

    @property
    def score(self) -> int:
        """Computed in code from the BANT judgements (25 points each). In testing the model, asked for a
        0-100 score directly, answered on a 0-10 scale, so no lead ever passed the threshold."""
        return 25 * (self.budget + self.authority + self.need + self.timing)


class LeadState(BaseModel):
    leads: list[dict] = []
    scores: dict[str, LeadScore] = {}
    threshold: int = 70
    emails: dict[str, str] = {}


class LeadFlow(Flow[LeadState]):
    llm = ollama_llm(DEFAULT_MODEL, temperature=0)

    @start()
    def load_leads(self):
        with open(HERE / "leads.csv", encoding="utf-8") as f:
            self.state.leads = list(csv.DictReader(f))
        print(f"[load] {len(self.state.leads)} leads")

    @listen(load_leads)
    def score_leads(self):
        scorer = Agent(role="Sales Development Rep", goal="Score inbound leads with BANT",
                       backstory=f"You sell {PRODUCT}. You are strict: students and 'maybe next year' score low.",
                       llm=self.llm)
        for lead in self.state.leads:
            s = scorer.kickoff(f"Score this lead:\n{lead}", response_format=LeadScore).pydantic
            self.state.scores[lead["email"]] = s
            print(f"[score] {s.score:>3} {lead['name']:<12} BANT={int(s.budget)}{int(s.authority)}"
                  f"{int(s.need)}{int(s.timing)} - {s.reason}")

    @router(score_leads)
    def has_hot_leads(self):
        hot = [e for e, s in self.state.scores.items() if s.score >= self.state.threshold]
        return "hot" if hot else "none"

    @listen("hot")
    def write_emails(self):
        writer = Agent(role="Account Executive", goal="Write personal first-contact emails",
                       backstory="You reference the lead's own words and propose one concrete next step.",
                       llm=ollama_llm(DEFAULT_MODEL, temperature=0.5))
        for lead in self.state.leads:
            if self.state.scores[lead["email"]].score >= self.state.threshold:
                self.state.emails[lead["email"]] = writer.kickoff(
                    f"Product: {PRODUCT}\nLead: {lead}\nWrite a 100-word email proposing a 30-minute call.").raw

    @listen("none")
    def nothing_to_do(self):
        print("No hot leads this time; all leads go to the nurture newsletter.")


def main() -> None:
    p = argparse.ArgumentParser(description="CrewAI lead-scoring flow")
    p.add_argument("--threshold", type=int, default=70, help="score needed to get a sales email (0-100)")
    a = p.parse_args()
    if not 0 <= a.threshold <= 100:
        print("--threshold must be 0-100")
        sys.exit(1)
    flow = LeadFlow()
    flow.kickoff(inputs={"threshold": a.threshold})
    for email, body in flow.state.emails.items():
        print(f"\n===== Email to {email} =====\n{body}")


if __name__ == "__main__":
    main()
