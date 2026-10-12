# Agent 33 - Instagram Post Generator (CrewAI, hierarchical)

## What it does
Describe a product and audience. It produces 3 Instagram posts, each with a caption, 5 hashtags and an image-generation prompt.

## Concepts you learn
- **Hierarchical process:** `Process.hierarchical` with `manager_llm=...`. You give ONE task to the crew, and CrewAI creates a manager agent that plans the work, delegates sub-tasks to the members (trend scout, copywriter, art director) and checks their results. Compare with `Process.sequential` (Agents 26, 27, 29) where you assign every task yourself.
- **When to use it:** when you don't want to hard-code the order of work, or the task needs back-and-forth between specialists.
- **Temperature per role:** the creative crew uses 0.6, the manager 0.2 to keep its decisions stable.

## The crew
```
           Manager (auto-created)
         /         |            \
Trend Scout   Copywriter   Art Director
(web_search)
```

## Run
```
cd 50-agents-for-all
.venv-crewai\Scripts\python.exe 03_crewai\33_instagram_post_generator\main.py "reusable bamboo coffee cups" --audience "young professionals"
```
Empty product exits with code 1.

## Things to try
- Watch the verbose log to see the manager's "Delegate work to coworker" calls.
- Switch to `Process.sequential` (you'll need one task per agent) and compare.
- Feed an image prompt into an image model (for example a local Stable Diffusion).

## Known limits
- Hierarchical runs make more LLM calls than sequential ones and are slower.
- The manager may skip a member (for example not use the trend scout) if it thinks it is not needed.
