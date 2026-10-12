# Agent 24 - Plan-and-Execute (LangGraph)

## What it does
For multi-step tasks, a planner first writes a step-by-step plan. An executor agent (with web search) carries out one step at a time, and a re-planner looks at the results and either finishes with an answer or updates the remaining steps.

## Concepts you learn
- **Plan first, act second:** better than a single agent loop for long tasks because the plan keeps it on track.
- **Subgraph as a node:** the executor is a complete tool-using agent made with `create_agent` from `langchain.agents`, called inside the `execute` node.
- **Accumulating state:** `past_steps: Annotated[list, operator.add]` appends each step's result instead of overwriting.
- **Re-planning:** structured output `Replan` either returns `final_answer` or `remaining_steps`.

## The graph
```
START -> planner -> execute -> replan --(more steps)--> execute
                                     \--(answer)--> END
```
`MAX_STEPS = 5` caps the work.

## Run
```
cd 50-agents-for-all
.venv-langgraph\Scripts\python.exe langgraph\24_plan_and_execute\main.py "Find the height of the Eiffel Tower and the Empire State Building and say which is taller and by how many meters."
```
Empty task exits with code 1.

## Things to try
- Give a task with a clear order ("Find X, then use it to find Y").
- Lower `MAX_STEPS` to 2.

## Known limits
- A capable executor may do several steps at once (in a test, step 1 answered everything and the re-planner finished early). That is efficient, but it hides the planning behaviour.
- The planner doesn't always respect "2 to 4 steps".
