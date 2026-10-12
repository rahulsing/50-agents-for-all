import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import common.crewai_env  # noqa: F401  (must come before crewai)

from crewai import Agent, Crew, Process, Task
from crewai.tools import tool

from common.crewai_env import ollama_llm
from common.llm import DEFAULT_MODEL

DEFAULT_FILE = Path(__file__).parent / "sample.md"
MAX_LINE = 120


def lint(text: str) -> list[str]:
    """Deterministic Markdown checks; the agent explains and fixes, the code finds."""
    issues, prev_level, headings, in_code, bullets = [], 0, set(), False, set()
    for n, line in enumerate(text.splitlines(), 1):
        if line.startswith("```"):
            in_code = not in_code
            if in_code and line.strip() == "```":
                issues.append(f"line {n}: code block has no language (e.g. ```bash)")
            continue
        if in_code:
            continue
        if line != line.rstrip():
            issues.append(f"line {n}: trailing whitespace")
        if len(line) > MAX_LINE:
            issues.append(f"line {n}: line longer than {MAX_LINE} characters")
        if m := re.match(r"^(#+)(\s*)(.*)", line):
            level, space, title = len(m.group(1)), m.group(2), m.group(3).strip()
            if not space:
                issues.append(f"line {n}: no space after '#' in heading")
            elif len(space) > 1:
                issues.append(f"line {n}: multiple spaces after '#' in heading")
            if prev_level and level > prev_level + 1:
                issues.append(f"line {n}: heading jumps from level {prev_level} to {level}")
            if title.lower() in headings:
                issues.append(f"line {n}: duplicate heading '{title}'")
            headings.add(title.lower())
            prev_level = level
        if m := re.match(r"^\s*([*+-])\s", line):
            bullets.add(m.group(1))
            if len(bullets) > 1:
                issues.append(f"line {n}: mixed list markers ({', '.join(sorted(bullets))})")
        if re.search(r"\[[^\]]*\]\([^)]*$", line):
            issues.append(f"line {n}: link is missing its closing ')'")
    return issues


@tool("lint_markdown")
def lint_markdown(path: str) -> str:
    """Run Markdown lint rules on a file and return the list of issues with line numbers."""
    p = Path(path)
    if not p.is_file():
        return f"File not found: {path}"
    issues = lint(p.read_text(encoding="utf-8"))
    return "\n".join(issues) if issues else "No issues found."


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_FILE
    if not path.is_file():
        print(f"File not found: {path}")
        sys.exit(1)
    reviewer = Agent(role="Documentation Reviewer", goal="Make Markdown files clean and consistent",
                     backstory="You rely on the lint tool for problems and explain each one simply.",
                     tools=[lint_markdown], llm=ollama_llm(DEFAULT_MODEL, temperature=0), allow_delegation=False,
                     verbose=True)
    task = Task(description=f"Run lint_markdown on '{path.resolve()}'. Then: 1) a table of issues "
                            "(line, problem, how to fix), 2) the full corrected file in a ```markdown block. "
                            f"Original file:\n{path.read_text(encoding='utf-8')}",
                expected_output="Issue table and corrected Markdown.", agent=reviewer)
    print(Crew(agents=[reviewer], tasks=[task], process=Process.sequential).kickoff().raw)


if __name__ == "__main__":
    main()
