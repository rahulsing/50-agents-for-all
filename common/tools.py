"""Plain-Python tool functions shared by several agents. Each framework wraps them in its own tool format."""
import ast
import operator

from ddgs import DDGS

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.Pow: operator.pow, ast.Mod: operator.mod, ast.USub: operator.neg}


def web_search(query: str, max_results: int = 4) -> str:
    """Search the web with the ddgs metasearch library (no API key); returns title, snippet and URL per result.

    Free search endpoints sometimes return nothing or rate-limit, so several backends are tried in turn."""
    error = None
    for backend in ("auto", "duckduckgo", "bing", "brave"):
        try:
            results = DDGS().text(query, max_results=max_results, backend=backend)
        except Exception as e:  # noqa: BLE001 - try the next backend, report the last error to the model
            error = e
            continue
        if results:
            return "\n".join(f"- {r['title']}: {r['body']} ({r['href']})" for r in results)
    return f"Search failed: {error or 'no results'}"


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("only numbers and + - * / ** % are allowed")


def calculate(expression: str) -> str:
    """Safely evaluate an arithmetic expression such as '(1200 * 0.15) / 3' (no eval of arbitrary code)."""
    try:
        return str(_eval(ast.parse(expression.replace(",", ""), mode="eval").body))
    except Exception as e:  # noqa: BLE001
        return f"Error: {e}"
