# Agent 31 - Email Auto Responder (CrewAI Flow)

## What it does
Reads the emails in `inbox/`, classifies each (billing, feature request, support, spam) and flags urgent ones, alerts on-call for urgent emails, and drafts replies for everything except spam. Drafts are saved in `drafts/` for a human to review; nothing is sent.

## Concepts you learn
- **CrewAI Flows:** event-driven code instead of a crew. `@start()` runs first, `@listen(x)` runs when `x` finishes, `@router(x)` returns a label that chooses the next path, `or_(a, "label")` runs after either.
- **Typed flow state:** `Flow[EmailState]` keeps emails, triage results and drafts in one Pydantic object shared by all steps.
- **Agents inside steps:** `Agent.kickoff(prompt, response_format=Triage)` calls one agent directly with structured output, no crew needed.
- **Human in the loop by design:** drafts only; a person sends them.

## The flow
```
load_inbox -> triage_emails -> any_urgent? --"urgent"--> alert_on_call --+
                                          \--"normal"--------------------+--> draft_replies
```

## Run
```
cd 50-agents-for-all
.venv-crewai\Scripts\python.exe 03_crewai\31_email_auto_responder\main.py
```
Add your own `.txt` emails to `inbox/`. An empty inbox exits with code 1.

## Things to try
- Remove `004_outage.txt` and see the router take the "normal" path.
- Add a category (for example "partnership") to the `Triage` model.
- Call `EmailFlow().plot()` to draw the flow as an HTML diagram.

## Known limits
- Early drafts promised refunds and invented a phone number; the writer's rules now forbid that, but always review drafts.
- Emails are triaged one by one (slower for a big inbox).
