# Agent 27 - Job Posting Generator (CrewAI)

## What it does
Give a company, a role and notes from the hiring manager. A researcher looks up the company on the web, a writer drafts the posting, and a reviewer removes biased wording, trims requirements and keeps it under 400 words. The final posting is printed and saved to `output/job_posting.md`.

## Concepts you learn
- **A writer + reviewer pair:** a second agent whose only job is quality control is a cheap way to improve output.
- **Saving task output:** `Task(output_file=...)` makes CrewAI write that task's result to a file automatically.
- **Inclusive-language rules in the backstory:** the reviewer checks for gendered words and unrealistic requirement lists.
- **Shared helpers:** `common/crewai_env.py` (telemetry off, UTF-8 console, Ollama LLM) and `common/tools.py` (web search with fallbacks).

## Guardrails (CrewAI task guardrails)
Search `main.py` for `GUARDRAIL` to find them. Both are attached to the review task: `Task(..., guardrails=[posting_rules, FAIRNESS_RULE], guardrail_max_retries=3)`.

| Guardrail | Type | What it checks |
|-----------|------|----------------|
| `posting_rules` | Python function returning `(passed, result_or_feedback)` | Under 450 words; no biased or gendered words (rockstar, ninja, young, he/his...); has Responsibilities and Requirements sections; no invented salary figures |
| `FAIRNESS_RULE` | plain-English sentence; CrewAI turns it into an LLM check (`LLMGuardrail`) | No requirements based on age, gender, nationality, religion or family status |

If a guardrail fails, its feedback goes back to the reviewer agent, which must redo the task (up to 3 times). The `[guardrail]` lines in the log show each decision. If it still fails after the retries, CrewAI raises an error and the program exits with code 3. Function guardrails are exact and free; LLM guardrails catch meaning that rules can't, but cost a model call and can be wrong.

What testing showed:
- **A too-broad rule blocks forever.** The first salary rule matched *any* currency amount, so "customer deposits exceeding £25 billion" failed all 4 attempts and the run stopped. The rule now matches only pay (an amount next to "salary/pay" or followed by "per year/hour").
- **Feedback must be actionable.** "Cut it to under 450 words" produced the same 473-word text on every retry: small models can't count. The feedback now says what to cut (About us to 2 sentences, at most 4 bullets per section, no closing paragraph). In the next run the posting passed first time (425 words).
- **LLM guardrails are not deterministic.** `FAIRNESS_RULE` rejected a posting saying "Must be under 30 years old / Male candidates preferred" with a clear reason, but once rejected a clean posting too (it passed 3 of 3 retries afterwards). Put hard rules in code and use LLM guardrails for judgement calls.

## The crew
```
Company Researcher (web_search) -> Job Description Writer -> Hiring Content Reviewer -> output/job_posting.md
```

## Run
```
cd 50-agents-for-all
.venv-crewai\Scripts\python.exe 03_crewai\27_job_posting_generator\main.py "Monzo" --role "Data Analyst" --notes "hybrid, London, SQL and Python"
```
Empty company exits with code 1.

## Things to try
- Compare the writer's draft with the reviewer's version in the verbose log.
- Add a salary-benchmark researcher with web search.

## Known limits
- Company facts come from search snippets and can be out of date; check them.
- Benefits are invented unless you list them in `--notes`.
