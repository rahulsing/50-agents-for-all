# Agent 42 - Hierarchical Agent Teams (LangGraph)

## What it does
A top-level supervisor manages two teams. The research team (searcher + fact checker) gathers and verifies facts; the writing team (writer + editor) produces the text. Each team has its own supervisor deciding which member works next.

## Concepts you learn
- **Hierarchy = graphs inside graphs:** each team is a compiled `StateGraph` (a subgraph). The top graph treats a whole team as one node.
- **Why hierarchies:** one supervisor choosing among many workers gets confused; splitting into teams keeps each decision small.
- **Dynamic structured output:** `create_model(...)` builds a `Literal[...]` type from each team's member names, so the same supervisor code works for any team.
- **Hop limits:** `MAX_HOPS_PER_TEAM` stops a team from looping forever.

## The graph
```
top supervisor -> research_team [supervisor -> searcher | fact_checker] -> top
               -> writing_team  [supervisor -> writer | editor]         -> top -> END
```

## Run
```
cd 50-agents-for-all
.venv-langgraph\Scripts\python.exe langgraph\42_hierarchical_agent_teams\main.py "Write a 100-word blog post about the James Webb Space Telescope's biggest discoveries"
```
Empty task exits with code 1. Expect several minutes: many LLM calls.

## Things to try
- Add a third member to the writing team (for example an SEO optimiser).
- Add a third team (for example "design team" that writes image prompts).
- Compare with Agent 31 (one flat supervisor).

## Known limits
- Length instructions get lost through the layers (asked for 100 words, got about 400).
- Slow: every routing decision is an LLM call.
