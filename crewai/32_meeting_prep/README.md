# Agent 32 - Meeting Prep (CrewAI)

## What it does
Before a meeting with a company, four agents prepare a one-page briefing: company snapshot and recent news, attendee information, industry context, talking points, smart questions, likely objections with answers, and sources.

## Concepts you learn
- **Four-agent sequential crew:** two researchers work independently, a strategist combines both (`context=[t1, t2]`), and a writer merges everything (`context=[t1, t2, t3]`).
- **Goal-driven output:** the meeting objective (`--objective`) changes the talking points and questions, not the research.
- **Reliable search matters:** in testing, the free search sometimes returned "No results found" for every query, leaving the agents with nothing. `common/tools.py` now retries several search backends.

## The crew
```
Company Researcher --+
Industry Analyst ----+--> Meeting Strategist --> Briefing Writer --> one-page briefing
```

## Run
```
cd 50-agents-for-all
.venv-crewai\Scripts\python.exe crewai\32_meeting_prep\main.py "Duolingo" --objective "sell our analytics dashboard" --attendees "Head of Data"
```
Empty company exits with code 1.

## Things to try
- Run it for the same company with two different objectives and compare.
- Save the briefing with `output_file=` on the last task (see Agent 09).

## Known limits
- Information about named people is rarely found by web search and the model may guess; don't rely on attendee details.
- The strategist can mix up who is selling to whom (in a test some questions treated Duolingo as the buyer of language-learning tools rather than of "our analytics dashboard"). Be explicit in `--objective`, e.g. "we sell X to them".
- Takes several minutes (four agents, several searches).
