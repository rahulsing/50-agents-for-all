# Agent 26 - Trip Planner (CrewAI)

## What it does
Give it a city, number of days and interests. Three agents work in sequence and print a research list, a day-by-day itinerary and a budget estimate.

## Concepts you learn
- **CrewAI model:** a *crew* of role-based *agents*, each given *tasks*. You describe who each agent is (role, goal, backstory) instead of drawing a graph.
- **Sequential process:** tasks run in order; each task can receive earlier outputs through `context=[...]`.
- **Tools per agent:** only the researcher gets `web_search`. The planner and budgeter just reason over what they are handed.
- **Compare with Agent 01 and 11:** one agent with a tool (Agno), an agent in a graph (LangGraph), and now a team with roles (CrewAI).

## The crew
```
Researcher (web_search) --> Planner --> Budget Advisor
   8 places + 3 tips      day-by-day     cost table + savings
```

## How the code works (`main.py`)
1. `LLM(model="ollama/<model>", base_url=...)` points CrewAI at local Ollama through LiteLLM.
2. `@tool("web_search")` wraps DuckDuckGo (`ddgs`) so agents can call it. No API key needed.
3. Three `Agent`s define roles; three `Task`s define the work and expected output.
4. `context=[research]` and `context=[plan]` pass results down the chain.
5. `Crew(..., process=Process.sequential).kickoff()` runs it; the script prints each task's output.

## Run
```
cd 50-agents-for-all
.venv-crewai\Scripts\python.exe 03_crewai\26_trip_planner\main.py Lisbon --days 3 --interests "food, history"
```
`--days` accepts 1 to 7. Missing city prints a message and exits with code 1. A run takes a few minutes on a local model.

## Things to try
- Change a backstory (for example make the planner "obsessed with saving time") and compare itineraries.
- Give the planner `web_search` too and see whether it checks details.
- Add a fourth agent (for example a packing-list writer) with its own task.
- Swap `Process.sequential` for `Process.hierarchical` (needs a manager LLM).

## Known limits
- A 7B model invents details: the itinerary can mix up places (it put a Porto venue in Lisbon) and ignore the research. Check facts before trusting it.
- Search results are only as good as DuckDuckGo snippets.
- Telemetry is disabled in code; CrewAI's console emoji are made safe for the Windows terminal.
