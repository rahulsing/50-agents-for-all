import sys
from pathlib import Path
from typing import Literal

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import common.crewai_env  # noqa: F401  (must come before crewai)

from crewai import Agent
from crewai.flow.flow import Flow, listen, or_, router, start
from pydantic import BaseModel, Field

from common.crewai_env import ollama_llm
from common.llm import DEFAULT_MODEL

HERE = Path(__file__).parent
INBOX, DRAFTS = HERE / "inbox", HERE / "drafts"


class Triage(BaseModel):
    category: Literal["billing", "feature_request", "support", "spam"]
    urgent: bool = Field(description="True if the business is blocked or many users are affected")
    summary: str


class EmailState(BaseModel):
    emails: dict[str, str] = {}
    triage: dict[str, Triage] = {}
    drafts: dict[str, str] = {}


class EmailFlow(Flow[EmailState]):
    """A Flow is event-driven code: each step runs when the step it listens to finishes."""

    llm = ollama_llm(DEFAULT_MODEL, temperature=0)

    @start()
    def load_inbox(self):
        self.state.emails = {p.stem: p.read_text(encoding="utf-8") for p in sorted(INBOX.glob("*.txt"))}
        print(f"[load_inbox] {len(self.state.emails)} emails")

    @listen(load_inbox)
    def triage_emails(self):
        triager = Agent(role="Inbox Triage Specialist", goal="Classify support emails correctly",
                        backstory="You spot scams and urgent outages instantly.", llm=self.llm)
        for name, text in self.state.emails.items():
            t = triager.kickoff(f"Classify this email:\n{text}", response_format=Triage).pydantic
            self.state.triage[name] = t
            print(f"[triage] {name}: {t.category}, urgent={t.urgent} - {t.summary}")

    @router(triage_emails)
    def any_urgent(self):
        return "urgent" if any(t.urgent for t in self.state.triage.values()) else "normal"

    @listen("urgent")
    def alert_on_call(self):
        for name, t in self.state.triage.items():
            if t.urgent:
                print(f"\n!!! ALERT on-call engineer: {name} - {t.summary}\n")

    @listen(or_(alert_on_call, "normal"))
    def draft_replies(self):
        writer = Agent(role="Customer Support Writer", goal="Write short, kind, useful replies",
                       backstory="You never promise refunds, dates or fixes; you say which team will review it. "
                                 "You never invent phone numbers, links, names or ticket numbers.", llm=self.llm)
        DRAFTS.mkdir(exist_ok=True)
        for name, text in self.state.emails.items():
            t = self.state.triage[name]
            if t.category == "spam":
                print(f"[draft] {name}: skipped (spam)")
                continue
            reply = writer.kickoff(f"Category: {t.category}. Urgent: {t.urgent}.\nWrite a reply (under 90 words, "
                                   f"signed 'Support Team') to this email:\n{text}").raw
            self.state.drafts[name] = reply
            (DRAFTS / f"{name}_reply.txt").write_text(reply, encoding="utf-8")
            print(f"[draft] {name}: saved")
        return self.state.drafts


def main() -> None:
    if not INBOX.is_dir() or not any(INBOX.glob("*.txt")):
        print(f"No emails found in {INBOX}")
        sys.exit(1)
    flow = EmailFlow()
    flow.kickoff()
    for name, reply in flow.state.drafts.items():
        print(f"\n===== {name} =====\n{reply}")
    print(f"\nDrafts saved in {DRAFTS} for a human to review before sending.")


if __name__ == "__main__":
    main()
