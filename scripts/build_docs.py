"""Build the tutorial website from the agent folders.

    python scripts/build_docs.py      # writes docs/ and mkdocs.yml
    mkdocs serve                       # preview at http://127.0.0.1:8000
    mkdocs gh-deploy --force           # publish to the gh-pages branch (GitHub Pages)

Each agent page = the agent's README.md + every .py file in its folder. Agent names, frameworks and industries
come from INDEX.md, so INDEX.md stays the single source of truth.
"""
import posixpath
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SRC = ROOT / "site_src"
REPO = "https://github.com/rahulsing/50-agents-for-all"
BLOB = f"{REPO}/blob/main"

FRAMEWORKS = {  # folder -> (title, one-paragraph introduction)
    "01_agno": ("Agno", "Agno builds an agent from a model, tools and instructions, with batteries included: memory "
                     "and sessions (SQLite), knowledge bases (vector DBs), structured output and guardrails. "
                     "Plain Python functions become tools automatically."),
    "02_langgraph": ("LangGraph", "LangGraph models an agent as a graph: nodes are steps (functions or LLM calls), "
                               "edges are decisions, and all nodes share a typed state. Loops, retries, "
                               "human approval and multi-agent hierarchies are all just graph shapes."),
    "03_crewai": ("CrewAI", "CrewAI describes a crew of role-played agents (role, goal, backstory) that work through "
                         "tasks, sequentially or under a manager. Flows add event-driven control with "
                         "@start, @listen and @router."),
    "04_autogen": ("AutoGen", "AutoGen (0.7) builds agents that talk to each other in teams: round-robin, "
                           "LLM-selected speakers, nested teams and 'society of mind'. The conversation is "
                           "the program."),
    "05_llamaindex": ("LlamaIndex", "LlamaIndex is a data framework for retrieval: load documents, build vector, "
                                 "summary or SQL indexes, and query them, or give the indexes to an agent as tools."),
    "06_anthropic_sdk": ("No framework (Anthropic SDK)", "The same research agent written with only the Anthropic "
                                                      "SDK pointed at Ollama, so you can see the agent loop that "
                                                      "frameworks hide."),
    "07_protocols": ("Protocols: MCP, A2A, REST", "How agents connect to the outside world: MCP serves tools to any "
                                               "agent, A2A lets agents discover and call other agents, and a REST "
                                               "API lets any program call an agent."),
}
GUARDRAIL_AGENTS = {"10", "18", "27", "42"}


def parse_index() -> list[dict]:
    """Read the agent rows of INDEX.md: | # | [Name](path/) | Framework | Industry | What it does |"""
    rows = []
    row = re.compile(r"^\| (\d\d) \| \[(.+?)\]\((.+?)/\) \| (.+?) \| (.+?) \| (.+?) \|$")
    for line in (ROOT / "INDEX.md").read_text(encoding="utf-8").splitlines():
        m = row.match(line)
        if m:
            num, name, path, framework, industry, desc = m.groups()
            desc = re.sub(r"\]\((?!https?:)([^)]+)\)", rf"]({BLOB}/\1)", desc)  # file links -> GitHub
            rows.append({"num": num, "name": name, "path": path, "framework": framework, "industry": industry,
                         "desc": desc.replace("**[Guardrail]** ", "")})
    return rows


def page_path(agent_path: str) -> str:
    return f"agents/{agent_path}.md"


def link(from_page: str, to_page: str) -> str:
    """Relative link between two pages (the site is served under /50-agents-for-all/, so no absolute links)."""
    return posixpath.relpath(to_page, posixpath.dirname(from_page) or ".")


def fix_links(md: str, folder: Path, agents_by_folder: dict, here: str) -> str:
    """Relative links in READMEs point at files in the repo; on the website they must point somewhere valid."""
    def repl(m):
        text, target = m.group(1), m.group(2)
        if re.match(r"^(https?:|#|mailto:)", target):
            return m.group(0)
        resolved = (folder / target).resolve()
        rel = resolved.relative_to(ROOT).as_posix() if resolved.is_relative_to(ROOT) else target
        if rel.rstrip("/") in agents_by_folder:  # link to another agent -> its page
            return f"[{text}]({link(here, page_path(rel.rstrip('/')))})"
        return f"[{text}]({BLOB}/{rel})"  # any other file -> GitHub
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", repl, md)


def code_block(path: Path, title: str) -> str:
    lang = {".py": "python", ".json": "json", ".md": "markdown", ".csv": "text", ".txt": "text"}.get(path.suffix, "")
    return f'```{lang} title="{title}" linenums="1"\n{path.read_text(encoding="utf-8").rstrip()}\n```\n'


def agent_page(agent: dict, agents_by_folder: dict) -> str:
    folder = ROOT / agent["path"]
    readme = (folder / "README.md").read_text(encoding="utf-8")
    here = page_path(agent["path"])
    readme = fix_links(readme, folder, agents_by_folder, here)
    title, _, body = readme.partition("\n")
    meta = (f"**Framework:** {agent['framework']} &nbsp;·&nbsp; **Industry:** {agent['industry']} "
            f"&nbsp;·&nbsp; [Source folder on GitHub]({REPO}/tree/main/{agent['path']})\n")
    if agent["num"] in GUARDRAIL_AGENTS:
        meta += ('\n!!! tip "Guardrails"\n    This agent demonstrates guardrails. Search the code below for '
                 f"`GUARDRAIL`, and see the [Guardrails overview]({link(here, 'guardrails.md')}).\n")
    parts = [title, "", meta, body.strip(), "", "## The code", ""]
    py_files = sorted(folder.glob("*.py"), key=lambda p: (p.name not in ("main.py", "server.py", "api.py"), p.name))
    if agent["path"] in ("07_protocols/54_notes_mcp_agno", "07_protocols/55_notes_mcp_langgraph"):
        py_files.append(ROOT / "07_protocols" / "notes_mcp_server.py")  # the shared MCP server
    for f in py_files:
        parts.append(code_block(f, f.relative_to(ROOT).as_posix()))
    data = [p for p in sorted(folder.rglob("*")) if p.is_file() and p.suffix not in (".py", ".pyc")
            and p.name not in ("README.md",) and "__pycache__" not in p.parts]
    if data:
        parts += ["### Other files", ""]
        parts += [f"- [`{p.relative_to(folder).as_posix()}`]({BLOB}/{p.relative_to(ROOT).as_posix()})" for p in data]
        parts.append("")
    parts.append(f"Install: `pip install -r {agent['path']}/requirements.txt` "
                 f"(shared by all agents of this framework; see [Getting started]({link(here, 'getting-started.md')})).")
    return "\n".join(parts) + "\n"


def framework_page(key: str, agents: list[dict]) -> str:
    title, intro = FRAMEWORKS[key]
    lines = [f"# {title}", "", intro, "", "| # | Agent | Industry | What it does |", "|---|---|---|---|"]
    for a in agents:
        tag = " **[Guardrail]**" if a["num"] in GUARDRAIL_AGENTS else ""
        lines.append(f"| {a['num']} | [{a['name']}]({link(f'frameworks/{key}.md', page_path(a['path']))}){tag} | "
                     f"{a['industry']} | {a['desc']} |")
    if key == "07_protocols":
        lines += ["", fix_links((ROOT / "07_protocols" / "README.md").read_text(encoding="utf-8").split("\n", 1)[1],
                                ROOT / "07_protocols", {}, f"frameworks/{key}.md")]
    return "\n".join(lines) + "\n"


def index_page(agents: list[dict]) -> str:
    lines = ["# Agent index", "", "All 58 agents, numbered in folder order (framework by framework).", "",
             "| # | Agent | Framework | Industry | What it does |", "|---|---|---|---|---|"]
    for a in agents:
        tag = " **[Guardrail]**" if a["num"] in GUARDRAIL_AGENTS else ""
        lines.append(f"| {a['num']} | [{a['name']}]({page_path(a['path'])}){tag} | {a['framework']} | "
                     f"{a['industry']} | {a['desc']} |")
    return "\n".join(lines) + "\n"


def shared_code_page() -> str:
    parts = ["# Shared code", "", "Helpers in `common/` used by many agents. Every agent imports model names "
             "from `common/llm.py`, so you can switch models in one place.", ""]
    for f in sorted((ROOT / "common").glob("*.py")):
        parts.append(code_block(f, f"common/{f.name}"))
    return "\n".join(parts)


def mkdocs_yml(by_fw: dict) -> str:
    nav = ["  - Home: index.md", "  - Getting started: getting-started.md", "  - How to read an agent: how-to-read.md"]
    for key in FRAMEWORKS:  # numbered folder order
        title = FRAMEWORKS[key][0]
        nav.append(f"  - '{title}':")
        nav.append(f"    - Overview: frameworks/{key}.md")
        for a in by_fw[key]:
            nav.append(f"    - '{a['num']} {a['name'].replace(chr(39), '')}': {page_path(a['path'])}")
    nav += ["  - Guardrails: guardrails.md", "  - Lessons learned: lessons.md", "  - Shared code: shared-code.md",
            "  - Agent index: agent-index.md"]
    return f"""# Generated by scripts/build_docs.py - edit that script, not this file.
site_name: 58 AI Agents on Your Own Computer
site_description: Learn AI agents by reading and running 58 small examples on local Ollama models.
site_url: https://rahulsing.github.io/50-agents-for-all/
repo_url: {REPO}
repo_name: rahulsing/50-agents-for-all
edit_uri: ""
theme:
  name: material
  features: [navigation.sections, navigation.top, navigation.footer, search.highlight, content.code.copy,
             content.tabs.link, toc.follow]
  palette:
    - scheme: default
      primary: indigo
      toggle: {{icon: material/weather-night, name: Dark mode}}
    - scheme: slate
      primary: indigo
      toggle: {{icon: material/weather-sunny, name: Light mode}}
markdown_extensions:
  - admonition
  - attr_list
  - md_in_html
  - tables
  - toc: {{permalink: true}}
  - pymdownx.details
  - pymdownx.superfences
  - pymdownx.highlight: {{anchor_linenums: true}}
  - pymdownx.inlinehilite
  - pymdownx.tabbed: {{alternate_style: true}}
plugins:
  - search
nav:
""" + "\n".join(nav) + "\n"


def main() -> None:
    if DOCS.exists():
        shutil.rmtree(DOCS)
    agents = parse_index()
    by_folder = {a["path"]: a for a in agents}
    by_fw: dict[str, list] = {k: [] for k in FRAMEWORKS}
    for a in agents:
        by_fw[a["path"].split("/")[0]].append(a)
        out = DOCS / page_path(a["path"])
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(agent_page(a, by_folder), encoding="utf-8")
    (DOCS / "frameworks").mkdir(parents=True)
    for key, items in by_fw.items():
        (DOCS / "frameworks" / f"{key}.md").write_text(framework_page(key, items), encoding="utf-8")
    for f in SRC.glob("*.md"):
        shutil.copy(f, DOCS / f.name)
    (DOCS / "assets").mkdir()
    shutil.copy(ROOT / "01_agno" / "01_research_agent" / "result.png", DOCS / "assets" / "agent01_result.png")
    (DOCS / "agent-index.md").write_text(index_page(agents), encoding="utf-8")
    (DOCS / "shared-code.md").write_text(shared_code_page(), encoding="utf-8")
    (ROOT / "mkdocs.yml").write_text(mkdocs_yml(by_fw), encoding="utf-8")
    print(f"Built {len(agents)} agent pages into {DOCS}")


if __name__ == "__main__":
    main()
