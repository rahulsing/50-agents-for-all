import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from llama_index.core import SQLDatabase
from llama_index.core.query_engine import NLSQLTableQueryEngine
from sqlalchemy import Column, Float, Integer, MetaData, String, Table, create_engine, insert

from common.llamaindex_setup import use_ollama

DEFAULT_CSV = Path(__file__).parent / "sales.csv"


def csv_to_sqlite(path: Path, table: str = "sales"):
    """Load a CSV into an in-memory SQLite table, guessing INTEGER / REAL / TEXT per column."""
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError("CSV has no rows")

    def kind(col):
        vals = [r[col] for r in rows]
        for typ, cast in ((Integer, int), (Float, float)):
            try:
                [cast(v) for v in vals]
                return typ, cast
            except ValueError:
                pass
        return String, str

    kinds = {c: kind(c) for c in rows[0]}
    engine = create_engine("sqlite://")
    meta = MetaData()
    t = Table(table, meta, *[Column(c, k[0]) for c, k in kinds.items()])
    meta.create_all(engine)
    with engine.begin() as con:
        con.execute(insert(t), [{c: kinds[c][1](r[c]) for c in r} for r in rows])
    return engine


def main() -> None:
    p = argparse.ArgumentParser(description="LlamaIndex natural-language questions over a CSV (text-to-SQL)")
    p.add_argument("question", nargs="?", default="")
    p.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    a = p.parse_args()
    if not a.question.strip():
        print('Please ask a question, e.g. main.py "Which region had the highest revenue?"')
        sys.exit(1)
    if not a.csv.is_file():
        print(f"CSV not found: {a.csv}")
        sys.exit(1)
    use_ollama()
    db = SQLDatabase(csv_to_sqlite(a.csv), include_tables=["sales"])
    # The engine shows the LLM the table schema, asks it for SQL, runs the SQL, then writes an answer from the rows
    engine = NLSQLTableQueryEngine(sql_database=db, tables=["sales"])
    response = engine.query(a.question.strip() + " (revenue = units * unit_price)")
    print(f"\nSQL: {response.metadata.get('sql_query', '?')}\n\n{response}")


if __name__ == "__main__":
    main()
