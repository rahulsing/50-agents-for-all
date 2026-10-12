# Agent 45 - Society of Mind (AutoGen)

## What it does
An inner team (writer + editor) drafts and revises a short text until the editor approves. From the outside, that team looks like a single agent called "author", whose one final message goes to a translator agent.

## Concepts you learn
- **SocietyOfMindAgent:** wraps a team so it behaves like one agent. Its inner messages stay hidden; a `response_prompt` turns the inner discussion into one clean answer.
- **Composition:** the outer `RoundRobinGroupChat([society, translator])` doesn't know the author is really two agents.
- **Agent vs tool:** compare with Agent 44, where an inner team is a *tool* the writer calls. Here the inner team is a *participant* in the outer chat.

## The structure
```
outer chat: [ author = (writer <-> editor until APPROVE) ] -> translator
```

## Run
```
cd 50-agents-for-all
.venv-autogen\Scripts\python.exe 04_autogen\45_society_of_mind\main.py "Write a short welcome message for new gym members" --language French
```
Empty task exits with code 1.

## Things to try
- Add a third inner agent (for example a fact checker).
- Use a different model for the editor than for the writer.

## Known limits
- The editor may approve on the first draft, so you only see one round.
