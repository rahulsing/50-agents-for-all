# Agent 19 - Group Chat with a manager (AutoGen)

## What it does
Three agents (planner, researcher with web search, writer) share one conversation. A manager, itself an LLM, reads the conversation and picks who speaks next until the writer finishes with TERMINATE.

## Concepts you learn
- **SelectorGroupChat:** unlike `RoundRobinGroupChat` (fixed order, Agent 04), the next speaker is chosen by an LLM using each agent's `description` and the `selector_prompt`.
- **Descriptions matter:** the manager only sees each agent's `description` (not its system message) when choosing.
- **allow_repeated_speaker=False:** prevents the same agent talking twice in a row.
- **Termination conditions combine with `|`:** stop when the writer says TERMINATE, or after 12 messages.

## The chat
```
user task -> manager picks: planner -> researcher (web_search) -> writer -> TERMINATE
```

## Run
```
cd 50-agents-for-all
.venv-autogen\Scripts\python.exe autogen\19_group_chat\main.py "Compare solar and wind power for a small farm in the UK"
```
Empty task exits with code 1.

## Things to try
- Add a fourth agent (for example a "critic") and update the selector prompt.
- Change the rules in `SELECTOR_PROMPT` (for example "the critic must speak before the writer").
- Swap to `RoundRobinGroupChat` and compare.

## Known limits
- Every turn costs an extra LLM call for the manager's choice.
- The writer may repeat the researcher's text rather than synthesise it.
