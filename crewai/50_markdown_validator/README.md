# Agent 50 - Markdown Validator (CrewAI)

## What it does
Checks a Markdown file (a deliberately messy `sample.md` is included), then explains every problem in a table (line, problem, fix) and outputs the corrected file.

## Concepts you learn
- **Deterministic tool + LLM explanation:** the `lint()` function finds problems with plain rules (heading spacing and level jumps, duplicate headings, mixed list markers, unclosed links, code blocks without a language, trailing spaces, long lines). The agent's job is to explain and fix, not to find. Rule-based checks are exact; LLMs are good at explaining and rewriting.
- **Single-agent crew:** a crew can have just one agent and one task; you still get CrewAI's tool handling and logging.
- **Testing the tool alone:** `lint()` is plain Python, so you can test it without any model (see "Things to try").

## The flow
```
file -> agent -> lint_markdown(path) -> list of issues -> issue table + corrected Markdown
```

## Run
```
cd 50-agents-for-all
.venv-crewai\Scripts\python.exe crewai\50_markdown_validator\main.py
.venv-crewai\Scripts\python.exe crewai\50_markdown_validator\main.py path\to\README.md
```
A missing file exits with code 1.

## Things to try
- Run just the rules: `.venv-crewai\Scripts\python.exe -c "import sys; sys.path.insert(0,'crewai/50_markdown_validator'); from main import lint, DEFAULT_FILE; print(lint(DEFAULT_FILE.read_text()))"`
- Add a rule (for example "image without alt text: `![](...)`").
- Point it at the READMEs in this repo.

## Known limits
- The rules are a small subset of real linters such as markdownlint.
- The corrected file is written by the model and can miss fixes the table lists (in a test it kept the duplicate "Usage" heading and the over-long line). Run the lint again on the result, and diff it before replacing anything.
