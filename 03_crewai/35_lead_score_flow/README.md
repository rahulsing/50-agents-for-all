# Agent 35 - Lead Score Flow (CrewAI Flow)

## What it does
Scores the inbound sales leads in `leads.csv` (fictional) for a fictional SaaS product using BANT (Budget, Authority, Need, Timing), prints a score and reason per lead, and writes a personal first-contact email for every lead above the threshold.

## Concepts you learn
- **Flow with a router:** `load_leads -> score_leads -> has_hot_leads` returns "hot" or "none", choosing between `write_emails` and `nothing_to_do`.
- **Flow inputs:** `flow.kickoff(inputs={"threshold": 70})` sets fields of the typed state (`LeadState`) before the flow starts.
- **The model judges, code scores:** `LeadScore` returns four BANT booleans and a reason; the 0-100 score is a Python property (25 points per criterion met). In the first version the model was asked for a 0-100 score directly and answered on a 0-10 scale (8, 0, 8, 1, 8), so no lead ever passed the threshold of 70 and the flow always took the "none" path.
- **Business rules in the backstory:** "students and 'maybe next year' score low" steers the scoring.

## The flow
```
load_leads -> score_leads -> has_hot_leads? --"hot"--> write_emails
                                            \--"none"--> nothing_to_do
```

## Run
```
cd 50-agents-for-all
.venv-crewai\Scripts\python.exe 03_crewai\35_lead_score_flow\main.py
.venv-crewai\Scripts\python.exe 03_crewai\35_lead_score_flow\main.py --threshold 90
```
`--threshold` outside 0-100 exits with code 1. A very high threshold shows the "none" path.

## Things to try
- Add leads to `leads.csv`, including tricky ones (a CEO of a 3-person company, a big company with no timeline).
- Weight the criteria differently (for example need and timing 35 points, budget and authority 15).

## Known limits
- Each BANT flag is still the model's judgement; read the reason line.
- Emails are drafts for a person to review and send.
