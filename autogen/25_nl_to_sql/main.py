import asyncio
import re
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import TerminatedException, TerminationCondition
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.messages import StopMessage, ToolCallExecutionEvent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console

from common.autogen_client import ollama_client
from common.llm import DEFAULT_MODEL
from common.sample_db import create_shop_db

DB = create_shop_db(Path(__file__).parent / "shop.db")
NUMBER = re.compile(r"\d[\d,]*\.?\d*")


def _ro():
    return sqlite3.connect(f"file:{DB}?mode=ro", uri=True)


def get_schema() -> str:
    """Return the CREATE TABLE statements for every table."""
    with _ro() as con:
        return "\n".join(r[0] for r in con.execute("SELECT sql FROM sqlite_master WHERE type='table'"))


def run_sql(sql: str) -> str:
    """Run one read-only SELECT and return up to 15 rows."""
    if not sql.strip().lower().startswith(("select", "with")):
        return "Error: only SELECT queries are allowed."
    try:
        with _ro() as con:
            cur = con.execute(sql)
            return f"{[d[0] for d in cur.description]}\n" + "\n".join(map(str, cur.fetchmany(15)))
    except sqlite3.Error as e:
        return f"SQL error: {e}"


def _numbers(text: str) -> set[float]:
    return {float(n.replace(",", "")) for n in NUMBER.findall(text) if n.replace(",", "").replace(".", "")}


class VerifiedApproval(TerminationCondition):
    """Stop only when the reviewer says APPROVED and the numbers in its answer appear together in ONE row of a
    real run_sql result.

    In testing, the reviewer wrote a correct query but then typed an imaginary result table instead of calling
    run_sql, and approved invented numbers ("12 orders, 10299") that were pieced together from two different
    real rows. This guard rejects such approvals, so the chat continues and the sql_writer gets another turn
    to actually run the corrected query."""

    def __init__(self) -> None:
        self._done = False
        self._real_rows: list[set[float]] = []

    @property
    def terminated(self) -> bool:
        return self._done

    async def __call__(self, messages):
        if self._done:
            raise TerminatedException("Termination condition has already been reached")
        for m in messages:
            if isinstance(m, ToolCallExecutionEvent):
                for result in m.content:
                    self._real_rows += [_numbers(line) for line in result.content.splitlines()[1:]]
            elif m.source == "reviewer" and "APPROVED" in m.to_text():
                claimed = _numbers(m.to_text().split("APPROVED")[0][-300:])  # numbers in the final answer
                if claimed and not any(claimed <= row for row in self._real_rows):
                    print(f"\n[guard] approval rejected: {sorted(claimed)} do not match any real run_sql row\n")
                    continue
                self._done = True
                return StopMessage(content="Approved with verified numbers", source="VerifiedApproval")
        return None

    async def reset(self) -> None:
        self._done = False
        self._real_rows = []


async def run(question: str) -> None:
    client = ollama_client(DEFAULT_MODEL)
    schema = get_schema()  # given up front: in testing the model guessed column names before reading the schema
    sql_writer = AssistantAgent(
        "sql_writer", model_client=client, tools=[run_sql], reflect_on_tool_use=True, max_tool_iterations=4,
        system_message=f"Turn the question into SQLite SQL for this schema:\n{schema}\n"
                       "Use only these column names. Call run_sql. If it returns an error, fix the SQL and call "
                       "it again. If the reviewer suggests corrected SQL, run that. Report the final SQL and copy "
                       "the result rows exactly. Never state numbers that run_sql did not return.")
    reviewer = AssistantAgent(
        "reviewer", model_client=client, tools=[run_sql], reflect_on_tool_use=True,
        system_message=f"Schema:\n{schema}\nYou verify the sql_writer's work. Check joins, filters and grouping, "
                       "and that the result has the shape the question asks for: a question about a total needs "
                       "ONE row, not one row per customer or product. If the SQL is wrong, give the corrected SQL "
                       "and ask the sql_writer to run it. You may run SQL yourself with run_sql, but never type a "
                       "result table yourself. Only if the SQL is right, give the final answer in one sentence "
                       "using numbers copied from a real run_sql result, and end with APPROVED.")
    team = RoundRobinGroupChat([sql_writer, reviewer],
                               termination_condition=VerifiedApproval() | MaxMessageTermination(9))
    await Console(team.run_stream(task=question))
    await client.close()


def main() -> None:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        print('Please ask a question, e.g. main.py "How many orders did customers in Paris place?"')
        sys.exit(1)
    asyncio.run(run(question))


if __name__ == "__main__":
    main()
