import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from common.llm import DEFAULT_MODEL, OLLAMA_URL
from common.sample_db import create_shop_db

DB = create_shop_db(Path(__file__).parent / "shop.db")

SYSTEM = """You answer questions about a shop database (SQLite).
Steps: 1) list_tables, 2) describe_table for the tables you need, 3) run_query with ONE SELECT statement.
If run_query returns an error, fix the SQL and try again. Then answer in one or two sentences and show the SQL you used."""


def connect_read_only() -> sqlite3.Connection:
    return sqlite3.connect(f"file:{DB}?mode=ro", uri=True)  # the agent can never modify data


@tool
def list_tables() -> str:
    """List the tables in the database."""
    with connect_read_only() as con:
        return ", ".join(r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'"))


@tool
def describe_table(table: str) -> str:
    """Show the columns of a table and 3 sample rows."""
    with connect_read_only() as con:
        cols = con.execute(f"PRAGMA table_info({table})").fetchall()
        if not cols:
            return f"No table named {table}"
        rows = con.execute(f"SELECT * FROM {table} LIMIT 3").fetchall()
    return f"columns: {[(c[1], c[2]) for c in cols]}\nsample: {rows}"


@tool
def run_query(sql: str) -> str:
    """Run one read-only SELECT query and return up to 20 rows."""
    if not sql.strip().lower().startswith(("select", "with")):
        return "Error: only SELECT queries are allowed."
    try:
        with connect_read_only() as con:
            cur = con.execute(sql)
            header = [d[0] for d in cur.description]
            return f"{header}\n" + "\n".join(map(str, cur.fetchmany(20)))
    except sqlite3.Error as e:
        return f"Error: {e}"


TOOLS = [list_tables, describe_table, run_query]


def build_graph():
    llm = ChatOllama(model=DEFAULT_MODEL, base_url=OLLAMA_URL, temperature=0).bind_tools(TOOLS)

    def agent(state: MessagesState):
        return {"messages": [llm.invoke([("system", SYSTEM)] + state["messages"])]}

    g = StateGraph(MessagesState)
    g.add_node("agent", agent)
    g.add_node("tools", ToolNode(TOOLS))
    g.add_edge(START, "agent")
    g.add_conditional_edges("agent", tools_condition)
    g.add_edge("tools", "agent")
    return g.compile()


def main() -> None:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        print('Please provide a question, e.g. main.py "Which city spent the most?"')
        sys.exit(1)
    final = ""
    for step in build_graph().stream({"messages": [("user", question)]}, {"recursion_limit": 20},
                                     stream_mode="values"):
        msg = step["messages"][-1]
        for call in getattr(msg, "tool_calls", None) or []:
            print(f"[tool call] {call['name']}({call['args']})")
        if msg.type == "ai" and msg.content:
            final = msg.content
    print("\n" + final)


if __name__ == "__main__":
    main()
