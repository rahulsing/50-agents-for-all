import argparse
import re
import sys
from pathlib import Path
from typing import Literal

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agno.agent import Agent
from agno.models.ollama import Ollama
from pydantic import BaseModel, Field

from common.llm import DEFAULT_MODEL, OLLAMA_URL

DEFAULT_DOC = Path(__file__).parent / "docs" / "sample_service_agreement.txt"


class Clause(BaseModel):
    title: str = Field(description="Clause name, e.g. 'Liability'")
    summary: str = Field(description="One plain-English sentence")
    risk_for_reviewer: Literal["low", "medium", "high"]
    reason: str = Field(description="Why this risk level, one sentence")


class Overview(BaseModel):
    parties: list[str]
    contract_type: str
    top_concerns: list[str] = Field(description="The 3 most important issues to negotiate, one sentence each")


def split_clauses(text: str) -> list[str]:
    """Split on lines that start with a clause number like '1.' so the model reviews one clause at a time."""
    parts = re.split(r"\n(?=\d+\.\s)", text)
    return [p.strip() for p in parts if re.match(r"\d+\.\s", p.strip())]


def make_agent(schema: type[BaseModel], side: str) -> Agent:
    return Agent(
        model=Ollama(id=DEFAULT_MODEL, host=OLLAMA_URL),
        instructions=[
            f"You review contracts on behalf of the {side}. Judge risk from the {side}'s point of view.",
            "Use only the given text; do not invent terms.",
        ],
        output_schema=schema,
    )


def main() -> None:
    p = argparse.ArgumentParser(description="Agno contract clause analyser")
    p.add_argument("file", nargs="?", default=str(DEFAULT_DOC))
    p.add_argument("--side", default="Client", help="which party you represent")
    a = p.parse_args()
    path = Path(a.file)
    text = path.read_text(encoding="utf-8").strip() if path.is_file() else ""
    if not text:
        print(f"File not found or empty: {path}")
        sys.exit(1)
    clauses = split_clauses(text)
    if not clauses:
        print("No numbered clauses found (expected lines starting with '1.', '2.', ...).")
        sys.exit(1)

    clause_agent = make_agent(Clause, a.side)
    reviewed: list[Clause] = []
    print(f"{'Clause':<24} {'Risk':<7} Summary")
    for c in clauses:
        result = clause_agent.run(f"Review this single clause:\n{c}").content
        if isinstance(result, Clause):
            reviewed.append(result)
            print(f"{result.title[:23]:<24} {result.risk_for_reviewer:<7} {result.summary}")
            print(f"{'':<32}why: {result.reason}")

    risky = "\n".join(f"- {r.title} ({r.risk_for_reviewer}): {r.reason}" for r in reviewed)
    overview = make_agent(Overview, a.side).run(f"Contract:\n{text[:1500]}\n\nClause risks:\n{risky}").content
    if isinstance(overview, Overview):
        print(f"\nParties: {', '.join(overview.parties)} | Type: {overview.contract_type} | Reviewing for: {a.side}")
        print("\nTop concerns:")
        print("\n".join(f"- {t}" for t in overview.top_concerns))
    print(f"\nReviewed {len(reviewed)} of {len(clauses)} clauses. Not legal advice; have a lawyer review real contracts.")


if __name__ == "__main__":
    main()
