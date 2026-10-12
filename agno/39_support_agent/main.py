import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agno.agent import Agent
from agno.exceptions import CheckTrigger, OutputCheckError
from agno.guardrails import PIIDetectionGuardrail, PromptInjectionGuardrail
from agno.knowledge.embedder.ollama import OllamaEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.models.ollama import Ollama
from agno.run.agent import RunOutput
from agno.run.base import RunStatus
from agno.vectordb.lancedb import LanceDb, SearchType
from pydantic import BaseModel, Field

from common.llm import DEFAULT_MODEL, EMBED_MODEL, OLLAMA_URL

HERE = Path(__file__).parent
TICKETS = HERE / "tickets.json"
EMBED_DIMS = 4096  # qwen3-embedding output size; change if you change EMBED_MODEL
EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", re.I)

# ----- GUARDRAILS ---------------------------------------------------------------------------------------
# Input guardrails run as pre_hooks, BEFORE the model sees the message. If one raises, the run stops and the
# model is never called. These two are Agno's built-in guardrails (agno.guardrails).
INPUT_GUARDRAILS = [
    PromptInjectionGuardrail(),  # blocks "ignore your instructions", "developer mode", "jailbreak", ...
    PIIDetectionGuardrail(
        enable_email_check=False,  # emails are allowed: the support flow needs one to open a ticket
        enable_phone_check=False,
        custom_patterns={"IBAN": r"\b[A-Z]{2}\d{2}(?:\s?[A-Z0-9]{4}){3,7}\b"},  # bank account numbers
    ),  # blocks card numbers, US SSNs and IBANs: customers must never send these to a support bot
]
LEAK_MARKERS = ("help-center references", "<references>", "system prompt", "instructions:")


def output_guardrail(run_output: RunOutput) -> None:
    """Custom output guardrail (a post_hook): runs AFTER the model answers, BEFORE the reply is used.

    Blocks replies that contain a card-like number or leak the agent's internal instructions."""
    text = str(run_output.content)
    if re.search(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", text):
        raise OutputCheckError("Reply contained a card-like number", check_trigger=CheckTrigger.OUTPUT_NOT_ALLOWED)
    if any(marker in text.lower() for marker in LEAK_MARKERS):
        raise OutputCheckError("Reply leaked internal instructions", check_trigger=CheckTrigger.OUTPUT_NOT_ALLOWED)
# --------------------------------------------------------------------------------------------------------


class SupportReply(BaseModel):
    answer: str = Field(description="Reply to the customer, based on the help-center references")
    section_used: str = Field(description="Help-center section the answer came from, or 'none'")
    escalate: bool = Field(description="True only if the references do not solve the problem, or the customer "
                                       "says they already tried those steps")
    ticket_summary: str = Field(description="One-sentence problem summary for a human agent, empty if not escalating")


def create_ticket(email: str, summary: str) -> str:
    tickets = json.loads(TICKETS.read_text(encoding="utf-8")) if TICKETS.exists() else []
    ticket = {"id": f"T{len(tickets) + 1:04d}", "email": email, "summary": summary,
              "created": datetime.now().isoformat(timespec="seconds")}
    tickets.append(ticket)
    TICKETS.write_text(json.dumps(tickets, indent=2), encoding="utf-8")
    return ticket["id"]


def build_knowledge() -> Knowledge:
    knowledge = Knowledge(
        vector_db=LanceDb(
            uri=str(HERE / "lancedb"),
            table_name="help_center",
            search_type=SearchType.vector,
            embedder=OllamaEmbedder(id=EMBED_MODEL, host=OLLAMA_URL, dimensions=EMBED_DIMS),
        ),
    )
    knowledge.insert(path=str(HERE / "kb"), skip_if_exists=True)  # embeds the help center once, then reuses it
    return knowledge


def build_agent() -> Agent:
    return Agent(
        model=Ollama(id=DEFAULT_MODEL, host=OLLAMA_URL),
        knowledge=build_knowledge(),
        add_knowledge_to_context=True,  # always retrieve: relevant help-center text is added to each request
        output_schema=SupportReply,
        pre_hooks=INPUT_GUARDRAILS,  # GUARDRAIL: checks the customer's message before the model runs
        post_hooks=[output_guardrail],  # GUARDRAIL: checks the model's reply before we use it
        instructions=[
            "You are CloudNote customer support. Be brief, friendly, and reply in English.",
            "Answer only from the help-center references you are given.",
            "Compare the customer's message with the help-center steps. If the customer has ALREADY done those "
            "steps, or the references do not cover the problem, set escalate to true and do not repeat the steps.",
        ],
    )


def main() -> None:
    message = " ".join(sys.argv[1:]).strip()
    if not message:
        print('Please provide a customer message, e.g. main.py "How do I get a refund?"')
        sys.exit(1)
    run = build_agent().run(message)
    if run.status == RunStatus.error:  # a guardrail stopped the run (Agno returns the error, it doesn't raise)
        print(f"\n[guardrail] Blocked: {run.content}")
        if "PII" in str(run.content):
            print("For your security, please don't share card numbers, bank details or ID numbers here.")
        elif "injection" in str(run.content):
            print("I can only help with questions about CloudNote.")
        else:
            print("Sorry, I can't send that reply. A human agent will follow up.")
        sys.exit(3)
    reply = run.content
    if not isinstance(reply, SupportReply):
        print("The model did not return a valid reply. Try again.")
        sys.exit(2)
    print(f"\n{reply.answer}\n\n[section: {reply.section_used} | escalate: {reply.escalate}]")

    # The model only DECIDES; plain code ACTS. A ticket needs a real email from the customer's own message.
    if reply.escalate:
        found = EMAIL.search(message)
        if found:
            ticket = create_ticket(found.group(0), reply.ticket_summary or message[:120])
            print(f"I've opened ticket {ticket} for our team; we'll email {found.group(0)}.")
        else:
            print("I'd like to pass this to our team. What email address should we contact you on?")


if __name__ == "__main__":
    main()
