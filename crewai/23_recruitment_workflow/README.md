# Agent 23 - Recruitment Workflow (CrewAI)

## What it does
Screens the CVs in `data/candidates/` against `data/job_description.txt`. Each must-have is checked against the CV with quoted evidence, a score is computed, then an interviewer writes targeted questions and HR writes a shortlist. All candidates are fictional.

## Concepts you learn
- **One document per task:** a screening task is created per CV, which is more reliable for small models than one prompt with every CV.
- **Evidence-based checks:** each requirement must cite "exact words from the CV" or say "not in CV", which reduces invented skills.
- **The model judges, code scores:** in the first version the model gave a score directly and rated a candidate missing 2 of 4 must-haves at 85/100. Now `score` is a Python property: the share of must-haves met. Numbers that matter should be computed, not generated.
- **Two crews in sequence:** a screening crew, then a reporting crew that receives the computed ranking.

## The flow
```
CV 1..N -> [CV Screener -> CandidateScore] -> code computes scores and ranks
        -> Interview Designer -> HR Coordinator -> shortlist
```

## Run
```
cd 50-agents-for-all
.venv-crewai\Scripts\python.exe crewai\23_recruitment_workflow\main.py
```
Missing job file or no CVs exits with code 1.

## Things to try
- Add your own (anonymised) CV as a `.txt` file.
- Change the must-haves in the job description and see the scores change.

## Known limits
- The model decides "met / not met", so borderline skills can still be judged wrongly; read the evidence lines. In a test, Ben's "basic SQL (online course)" was marked "not in CV".
- Real hiring decisions need a human; this is a screening aid only.
