# Agent 24 - Information Gathering (LangGraph)

## What it does
A chatbot that helps you design a reusable LLM prompt template. It asks questions until it knows four things (objective, variables, constraints, requirements), then generates the template with `{placeholders}`.

## Concepts you learn
- **A tool as a "form":** `PromptInstructions` is a Pydantic model bound as a tool. The model "calls" it only when every field is known; that call is the signal that gathering is done. Nothing is executed; the arguments are the collected data.
- **Two-phase graph:** `gather` (ask questions) and `write_prompt` (use the collected data). The router checks for the tool call.
- **Waiting for the user = ending the run:** when the bot asks a question, the graph goes to END. The next message continues the same conversation because of the checkpointer.
- **Checkpointer memory:** `InMemorySaver` + a `thread_id` keeps the conversation between turns.

## The graph
```
START -> gather --(PromptInstructions called)--> write_prompt -> END
               \--(asked a question)--> END (wait for the next user message)
```

## Run
```
cd 50-agents-for-all
.venv-langgraph\Scripts\python.exe 02_langgraph\24_information_gathering\main.py
```
Example answers: "a prompt that writes product descriptions for an online shop", "inputs are product name, key features and target customer", "avoid exaggerated claims, never mention competitors", "under 80 words, friendly tone, end with a call to action". Type `exit` to quit.

## Things to try
- Give everything in one message and see it skip the questions.
- Add a fifth field (for example `examples: list[str]`).

## Known limits
- The model may call the form before you answered every question and fill gaps itself (in a test it invented "informative, balanced" as requirements and missed the 80-word limit). Read the `[collected]` line.
