# Agent 47 - Multi-Agent Collaboration (LangGraph)

## What it does
Two agents share one conversation and pass the work back and forth: a researcher (web search, no maths) and an analyst (calculator, no search). They continue until the analyst gives the FINAL ANSWER.

## Concepts you learn
- **Collaboration without a supervisor:** the router just hands the baton to the other agent. Compare with Agent 31 (a supervisor decides) and Agent 42 (teams of teams).
- **Complementary tools:** each agent can do something the other can't, so they must cooperate.
- **Code-enforced sign-off:** in testing the researcher did the maths itself and declared FINAL ANSWER, so the analyst never ran. Now only the analyst may finish: a researcher's FINAL ANSWER still goes to the analyst, who recomputes with the calculator.
- **Turn limit:** `MAX_TURNS = 6` stops endless ping-pong.

## The graph
```
START -> researcher <-> analyst --(analyst says FINAL ANSWER)--> END
```

## Run
```
cd 50-agents-for-all
.venv-langgraph\Scripts\python.exe langgraph\47_multi_agent_collaboration\main.py "Find the populations of Tokyo and Delhi metro areas and compute the percentage difference"
```
Empty task exits with code 1.

## Things to try
- Give a task needing two rounds of search (the analyst asks the researcher for a missing number).
- Add a third agent and change the router to a cycle.

## Known limits
- The calculator makes the arithmetic exact, but the model still chooses the formula. In a test it computed |a - b| / (a + b) = 10.16%, which is not a standard "percentage difference" (dividing by the average gives about 20%). Say exactly which formula you want, or check it.
- Slow: in a test the hand-offs took about 11 minutes on a 7B model.
