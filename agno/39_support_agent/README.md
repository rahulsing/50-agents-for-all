# Agent 39 - Support Agent (Agno)

## What it does
Customer support for a fictional app (CloudNote). It answers from a help-center knowledge base and names the section it used. If the help center cannot solve the problem (or the customer already tried those steps), it opens a ticket in `tickets.json` using the email in the customer's message.

## Concepts you learn
- **Agno Knowledge + vector DB:** `Knowledge(vector_db=LanceDb(...))` embeds `kb/faq.md` once with Ollama embeddings and stores it on disk in `lancedb/`. `add_knowledge_to_context=True` retrieves the relevant text for every message.
- **The model decides, code acts:** earlier versions gave the model a `create_ticket` tool. The 7B model created tickets with made-up emails and even invented ticket ids without calling the tool; a 14B model called the tool but answered in Thai. The working design returns a structured `SupportReply` with an `escalate` flag, and plain Python creates the ticket only if there is a real email in the customer's message.
- **Why this matters:** for actions with side effects (tickets, refunds, emails), keep the final action in code you control.

## Guardrails (Agno built-in)
Search `main.py` for `GUARDRAIL` to find them.

| Guardrail | Type | When it runs | What it does |
|-----------|------|--------------|--------------|
| `PromptInjectionGuardrail()` | Agno built-in, `pre_hooks` | before the model | Blocks messages like "ignore your instructions", "developer mode", "jailbreak" |
| `PIIDetectionGuardrail(...)` | Agno built-in, `pre_hooks` | before the model | Blocks card numbers, US SSNs and IBANs (custom pattern). Emails and phone numbers are allowed because the ticket flow needs an email |
| `output_guardrail` | custom function, `post_hooks` | after the model | Rejects a reply containing a card-like number or leaked internal instructions |

When a guardrail fires, Agno stops the run and returns it with `status == RunStatus.error` (it does not raise), so `main.py` checks the status and prints a safe message (exit code 3). A blocked input never reaches the model, which also saves time.

## The flow
```
message -> retrieve help-center text -> model -> SupportReply {answer, section, escalate}
                                              -> escalate and email found? -> create ticket (code)
```

## Run
```
cd 50-agents-for-all
.venv-agno\Scripts\python.exe agno\39_support_agent\main.py "How do I get a refund and how long does it take?"
.venv-agno\Scripts\python.exe agno\39_support_agent\main.py "My notes have not synced for 3 days even after signing out and in and reinstalling. I'm sam@example.com"
```
Empty message prints a message and exits with code 1.

## Things to try
- Escalate without an email and see it ask for one.
- Edit `kb/faq.md`, delete the `lancedb` folder, and run again to re-embed.

## Known limits
- The first run is slower while it embeds the help center.
- `EMBED_DIMS` must match the embedding model (4096 for `qwen3-embedding`).
