# Agent 44 - Nested Chats (AutoGen)

## What it does
A writer agent writes a short marketing text, sends the draft to a review panel, and then writes the final version. The review panel is itself a conversation between two agents (a critic and a fact checker). That whole inner chat is used as ONE tool by the writer.

## Concepts you learn
- **Nested chats with TeamTool:** `TeamTool(team=review_team, ...)` wraps a complete team so another agent can call it like a function. The inner team runs its own conversation and returns its last message.
- **Encapsulation:** the writer doesn't know the panel has two members; you could swap the panel for a bigger team without changing the writer.
- **Tool arguments for small models:** the first version passed the user's request to `review_draft` instead of a draft. The tool description and prompt now say exactly what must go in the `task` argument.

## The structure
```
writer --calls--> review_draft tool == [critic <-> fact_checker] (inner chat) --feedback--> writer --> FINAL
```

## Run
```
cd 50-agents-for-all
.venv-autogen\Scripts\python.exe 04_autogen\44_nested_chats\main.py "Write an 80-word product description for a smart water bottle"
```
Empty task exits with code 1.

## Things to try
- Add a third reviewer (for example a brand-voice checker) to the inner team.
- Use `AgentTool` instead to wrap a single agent as a tool.
- Compare with Agent 45, where an inner team is wrapped as an *agent* instead of a tool.

## Known limits
- Small models don't always follow the process: in testing the writer once skipped the tool and once applied very little of the panel's feedback in its FINAL text. Compare the draft and the final.
- The inner chat repeats itself (the fact checker often restates the critic's points).
