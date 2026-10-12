import subprocess
import sys
import tempfile
from pathlib import Path
from typing import TypedDict

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from common.llm import CODER_MODEL, OLLAMA_URL

MAX_ATTEMPTS = 3
llm = ChatOllama(model=CODER_MODEL, base_url=OLLAMA_URL, temperature=0, num_ctx=16384)


class Code(BaseModel):
    prefix: str = Field(description="One or two sentences describing the approach")
    imports: str = Field(description="Only the import statements")
    code: str = Field(description="The code without imports. It must print a demonstration of the result.")


class State(TypedDict):
    task: str
    solution: Code | None
    error: str
    attempts: int


def generate(state: State) -> dict:
    prompt = f"Write a Python 3 solution (standard library only).\nTask: {state['task']}"
    if state["error"]:
        prev = state["solution"]
        prompt += (f"\n\nYour previous attempt failed.\nImports:\n{prev.imports}\nCode:\n{prev.code}\n"
                   f"Error:\n{state['error']}\nFix it.")
    sol = llm.with_structured_output(Code).invoke(prompt)
    print(f"\n[generate] attempt {state['attempts'] + 1}: {sol.prefix}")
    return {"solution": sol, "attempts": state["attempts"] + 1, "error": ""}


def run_python(source: str) -> tuple[bool, str]:
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(source)
    try:
        r = subprocess.run([sys.executable, f.name], capture_output=True, text=True, timeout=30)
        return r.returncode == 0, (r.stdout if r.returncode == 0 else r.stderr)[-1500:]
    except subprocess.TimeoutExpired:
        return False, "Timed out after 30 seconds."
    finally:
        Path(f.name).unlink(missing_ok=True)


def check(state: State) -> dict:
    sol = state["solution"]
    ok, out = run_python(sol.imports)
    if not ok:
        print(f"[check] import failed:\n{out}")
        return {"error": f"Import error: {out}"}
    ok, out = run_python(sol.imports + "\n\n" + sol.code)
    print(f"[check] {'passed' if ok else 'failed'}:\n{out.strip()[:800]}")
    return {"error": "" if ok else out}


def decide(state: State) -> str:
    if not state["error"] or state["attempts"] >= MAX_ATTEMPTS:
        return END
    return "generate"


def build_graph():
    g = StateGraph(State)
    g.add_node("generate", generate)
    g.add_node("check", check)
    g.add_edge(START, "generate")
    g.add_edge("generate", "check")
    g.add_conditional_edges("check", decide, ["generate", END])
    return g.compile()


def main() -> None:
    task = " ".join(sys.argv[1:]).strip()
    if not task:
        print('Please provide a coding task, e.g. main.py "A function that checks if a string is a palindrome"')
        sys.exit(1)
    out = build_graph().invoke({"task": task, "solution": None, "error": "", "attempts": 0})
    status = "WORKING" if not out["error"] else f"STILL FAILING after {out['attempts']} attempts"
    print(f"\n===== {status} =====\n{out['solution'].imports}\n\n{out['solution'].code}")


if __name__ == "__main__":
    main()
