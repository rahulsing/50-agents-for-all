# Agent 04 - Code Execution Feedback Loop (AutoGen)

## What it does
You describe a programming task. A **coder** agent writes a Python script, an **executor** agent runs it, and the output goes back to the coder. If the script fails, the coder sees the error and fixes it. It stops when the coder confirms the output is correct.

## Concepts you learn
- **AutoGen model:** agents talk to each other in a *team*; the conversation is the program.
- **RoundRobinGroupChat:** agents take turns in a fixed order (coder, executor, coder, ...).
- **Self-correction through feedback:** the model does not need to be right the first time, because real execution results correct it.
- **Termination conditions:** a team needs a rule for when to stop. Here: coder says TERMINATE after seeing output, or a maximum number of messages.

## The loop
```
task -> coder writes code -> executor runs it -> output/error -> coder
                                 ^                                  |
                                 +------- fix and resend ----------+
stop when coder replies TERMINATE (without code) or the message limit is hit
```

## How the code works (`main.py`)
1. `OllamaChatCompletionClient` connects AutoGen to local Ollama (model set by `CODER_MODEL` in `common/llm.py`, default `qwen3-coder:30b`).
2. `AssistantAgent("coder")` has a system prompt telling it to answer with one runnable script.
3. `CodeExecutorAgent("executor")` extracts the code block and runs it with `LocalCommandLineCodeExecutor` inside `workspace/`.
4. `DoneAfterExecution` is a small custom termination rule. Small models tend to write TERMINATE together with the code, before it has run; this rule ignores that and waits for a TERMINATE with no code in it.
5. `Console(team.run_stream(...))` prints every message so you can watch the loop.

## Run
```
cd 50-agents-for-all
.venv-autogen\Scripts\python.exe autogen\04_code_feedback_loop\main.py "Compute 17 factorial and print it"
```
Optional: `--max-messages 10` caps the conversation. An empty task prints a message and exits with code 1.

## Safety
The executor runs model-written code **on your machine**, with your user permissions, in `workspace/`. AutoGen prints a warning about this. Use simple tasks, read the code in the log, and do not ask for anything that deletes files or touches the network. Running it in Docker (`DockerCommandLineCodeExecutor`) is the safer upgrade.

## Things to try
- Ask for something that needs a library that is not installed and watch the coder react to the error.
- Lower `--max-messages` to 3 and see the loop get cut off.
- Change the system prompt to demand type hints or tests.
- Use a smaller model (`AGENT_MODEL` does not apply here; set `CODER_MODEL=qwen2.5:7b-instruct`) and compare reliability.

## Known limits
- The tested tasks (primes, factorial, file read/write) all passed on the first try, so the fix-after-error path is built but I did not see it triggered.
- The 30B model is slow to load the first time.
- Executor only handles Python code blocks in this setup.
