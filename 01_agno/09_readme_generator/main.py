import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.file import FileTools

from common.llm import DEFAULT_MODEL, OLLAMA_URL


def build_agent(project: Path) -> Agent:
    return Agent(
        model=Ollama(id=DEFAULT_MODEL, host=OLLAMA_URL),
        # Read-only file access, sandboxed to the project folder
        tools=[FileTools(base_dir=project, enable_save_file=False, enable_delete_file=False,
                         enable_replace_file_chunk=False, enable_read_file=True, enable_list_files=True,
                         enable_search_files=True)],
        instructions=[
            "You write README.md files for code projects.",
            "You are given the file list. Read the main source files (at most 4) with read_file before writing; "
            "paths are relative to the project root.",
            "If you cannot read the files, say so instead of guessing. Never invent files, libraries or commands.",
            "Write these sections: title and one-line description, Features, Requirements, "
            "How to run (exact commands from the code), Project structure, Notes.",
            "Only describe what you saw in the files. Output only the README markdown.",
        ],
        debug_mode=True,
    )


def main() -> None:
    p = argparse.ArgumentParser(description="Agno README generator")
    p.add_argument("project", nargs="?", default="")
    p.add_argument("--out", help="save the README here instead of only printing it")
    a = p.parse_args()
    project = Path(a.project).resolve() if a.project else None
    if not project or not project.is_dir():
        print("Please give a project folder, e.g. main.py ..\\07_shopping_partner")
        sys.exit(1)
    skip = {".db", ".pyc", ".lance", ".png", ".jpg"}
    files = sorted(str(f.relative_to(project)) for f in project.rglob("*")
                   if f.is_file() and f.suffix not in skip and "__pycache__" not in f.parts)[:40]
    prompt = f"Project folder name: {project.name}\nFiles (relative to the root):\n" + "\n".join(files)
    readme = build_agent(project).run(prompt + "\n\nRead the key files, then write the README.").content
    print(readme)
    if a.out:
        Path(a.out).write_text(readme, encoding="utf-8")
        print(f"\nSaved to {a.out}")


if __name__ == "__main__":
    main()
