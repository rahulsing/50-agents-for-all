# Agent 36 - Screenplay Writer (CrewAI)

## What it does
Turns a messy forum thread (`story.txt`, about an office "smart" coffee machine, with a spam line mixed in) into a short comedy scene in screenplay format.

## Concepts you learn
- **Pipeline of specialists:** a content cleaner (removes spam), a story analyst (characters, conflict, beats) and a screenwriter (formatting and comedy). Each task's output becomes the next one's `context`.
- **Different temperatures per role:** the cleaner runs at 0 (precise), the screenwriter at 0.7 (creative).
- **Pre-processing with an agent:** cleaning input before the creative step stops the spam line ending up in the script.

## The crew
```
Content Cleaner -> Story Analyst -> Screenwriter -> screenplay scene
```

## Run
```
cd 50-agents-for-all
.venv-crewai\Scripts\python.exe 03_crewai\36_screenplay_writer\main.py
.venv-crewai\Scripts\python.exe 03_crewai\36_screenplay_writer\main.py path\to\your_story.txt
```
A missing or empty file exits with code 1.

## Things to try
- Feed it a group-chat export or an email thread.
- Change the genre in the screenwriter's task ("film noir", "horror").
- Add a fourth agent that writes a one-line logline and a title.

## Known limits
- Screenplay formatting is approximate (no real page layout).
- A 7B model's humour is hit and miss.
