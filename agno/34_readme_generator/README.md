# Agent 34 - README Generator (Agno)

## What it does
Point it at a project folder. It reads the main files and writes a README (description, features, requirements, how to run, structure, notes). Use `--out` to save it.

## Concepts you learn
- **Sandboxed file tools:** `FileTools(base_dir=project, enable_save_file=False, enable_delete_file=False, ...)` lets the agent read files only inside that folder and never write or delete.
- **Give the model the map:** the first version let the model list files itself; it passed the wrong path, got nothing, and then invented a whole project. Now the code lists the files and puts them in the prompt, and the model only decides which to read. Doing the deterministic part in code is a recurring reliability trick.
- **"Say so instead of guessing":** an explicit instruction for what to do when tools fail.

## The flow
```
folder -> code lists files -> model -> read_file(main.py), read_file(...) -> README markdown
```

## Run
```
cd 50-agents-for-all
.venv-agno\Scripts\python.exe agno\34_readme_generator\main.py agno\26_shopping_partner
.venv-agno\Scripts\python.exe agno\34_readme_generator\main.py agno\26_shopping_partner --out generated_README.md
```
A missing folder prints a message and exits with code 1.

## Things to try
- Run it on other agent folders and compare with the hand-written READMEs.
- Switch to the larger coder model: `set AGENT_MODEL=qwen3-coder:30b`.

## Known limits
- Reads at most a few files; large projects get a shallow README.
- Small models still make up details (in a test it listed a non-existent package name and a requirements.txt that was not there). Review before publishing.
