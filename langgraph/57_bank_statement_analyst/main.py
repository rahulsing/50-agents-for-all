import argparse
import csv
import random
import statistics
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from typing import TypedDict

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

from common.llm import DEFAULT_MODEL, OLLAMA_URL

HERE = Path(__file__).parent
SAMPLE = HERE / "sample_statement.csv"
llm = ChatOllama(model=DEFAULT_MODEL, base_url=OLLAMA_URL, temperature=0)

# Known merchants are categorised by rules; unknown ones go to the LLM
RULES = {"TESCO": "Groceries", "LIDL": "Groceries", "ALDI": "Groceries", "SHELL": "Transport", "UBER": "Transport",
         "TFL": "Transport", "NETFLIX": "Subscriptions", "SPOTIFY": "Subscriptions", "RENT": "Housing",
         "BRITISH GAS": "Utilities", "THAMES WATER": "Utilities", "SALARY": "Income", "PRET": "Eating out",
         "DELIVEROO": "Eating out", "AMAZON": "Shopping"}


def make_sample(path: Path) -> None:
    """Synthetic statement for 3 months, with a few planted oddities. Not real data."""
    rng = random.Random(7)
    rows = []
    for month in (6, 7, 8):
        m0 = date(2026, month, 1)
        rows += [(m0, "SALARY ACME LTD", 3200.00), (m0 + timedelta(days=1), "RENT PAYMENT", -1250.00),
                 (m0 + timedelta(days=3), "BRITISH GAS", -85.40), (m0 + timedelta(days=5), "NETFLIX", -10.99),
                 (m0 + timedelta(days=5), "SPOTIFY", -11.99), (m0 + timedelta(days=9), "THAMES WATER", -38.00),
                 (m0 + timedelta(days=2), "CITY GYM", -35.00)]
        for _ in range(22):
            merchant, low, high = rng.choice([("TESCO", 12, 70), ("LIDL", 8, 45), ("PRET", 4, 12),
                                              ("UBER", 8, 25), ("TFL", 3, 9), ("AMAZON", 10, 60),
                                              ("DELIVEROO", 15, 35), ("BOOTS PHARMACY", 5, 25)])
            rows.append((m0 + timedelta(days=rng.randint(0, 28)), merchant, -round(rng.uniform(low, high), 2)))
    rows += [(date(2026, 7, 14), "AMAZON", -899.00),                    # unusually large
             (date(2026, 8, 2), "NETFLIX", -10.99),                     # duplicate charge in the same month
             (date(2026, 8, 19), "CRYPTOFX GLOBAL LTD", -450.00),       # new unknown merchant
             (date(2026, 8, 20), "CRYPTOFX GLOBAL LTD", -450.00)]
    rows.sort()
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "description", "amount"])
        w.writerows((d.isoformat(), desc, f"{amt:.2f}") for d, desc, amt in rows)


class Categories(BaseModel):
    mapping: dict[str, str]


class State(TypedDict):
    rows: list[dict]
    findings: dict
    report: str


def load(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [{"date": r["date"], "description": r["description"].upper(), "amount": float(r["amount"])}
                for r in csv.DictReader(f)]


def categorise(state: State) -> dict:
    unknown = sorted({r["description"] for r in state["rows"]
                      if not any(k in r["description"] for k in RULES)})
    llm_map = {}
    if unknown:
        llm_map = llm.with_structured_output(Categories).invoke(
            "Assign each bank-statement merchant one category from: Groceries, Transport, Subscriptions, "
            "Housing, Utilities, Eating out, Shopping, Health & Fitness, Investments, Other. "
            f"Return a mapping merchant -> category.\nMerchants: {unknown}").mapping
        print(f"[categorise] LLM labelled {len(llm_map)} unknown merchants: {llm_map}")
    for r in state["rows"]:
        rule = next((cat for key, cat in RULES.items() if key in r["description"]), None)
        r["category"] = rule or llm_map.get(r["description"], "Other")
    return {"rows": state["rows"]}


def analyse(state: State) -> dict:
    """Plain Python does the maths; the LLM never calculates totals."""
    spend, months, by_merchant = defaultdict(float), defaultdict(lambda: [0.0, 0.0]), defaultdict(list)
    for r in state["rows"]:
        m = r["date"][:7]
        if r["amount"] > 0:
            months[m][0] += r["amount"]
        else:
            months[m][1] += -r["amount"]
            spend[r["category"]] += -r["amount"]
            by_merchant[r["description"]].append(r)
    unusual = []
    for merchant, rs in by_merchant.items():
        amounts = [-r["amount"] for r in rs]
        med = statistics.median(amounts)
        unusual += [f"{r['date']} {merchant} {-r['amount']:.2f} (typical {med:.2f})"
                    for r in rs if len(rs) >= 3 and -r["amount"] > 4 * med]
        if len(rs) <= 2 and min(amounts) >= 200:
            unusual.append(f"New large merchant: {merchant}, {len(rs)} payments totalling {sum(amounts):.2f}")
        seen = defaultdict(int)
        for r in rs:
            seen[(r["date"][:7], r["amount"])] += 1
        if merchant in ("NETFLIX", "SPOTIFY") or any(k in merchant for k in ("GYM",)):
            unusual += [f"Possible duplicate subscription: {merchant} charged {n} times in {k[0]}"
                        for k, n in seen.items() if n > 1]
    findings = {
        "monthly": {m: {"in": round(v[0], 2), "out": round(v[1], 2), "saved": round(v[0] - v[1], 2)}
                    for m, v in sorted(months.items())},
        "spend_by_category": dict(sorted(((k, round(v, 2)) for k, v in spend.items()), key=lambda x: -x[1])),
        "top_3_categories": [k for k, _ in sorted(spend.items(), key=lambda x: -x[1])[:3]],
        "best_saving_month": max(months, key=lambda m: months[m][0] - months[m][1]),
        "worst_saving_month": min(months, key=lambda m: months[m][0] - months[m][1]),
        "unusual": unusual,
    }
    print(f"[analyse] {findings}")
    return {"findings": findings}


def write_report(state: State) -> dict:
    report = llm.invoke(
        "You are a friendly personal-finance assistant. Using ONLY these computed figures (do not recalculate), "
        "write: 1) a 3-sentence overview naming best_saving_month and worst_saving_month as given, "
        "2) the top_3_categories exactly as listed, with amounts, 3) each unusual transaction and what "
        "the user should check, 4) a simple monthly budget suggestion with 3 concrete savings tips. "
        "Use the currency GBP.\n\n" + str(state["findings"])).content
    return {"report": report}


def build_graph():
    g = StateGraph(State)
    g.add_node("categorise", categorise)
    g.add_node("analyse", analyse)
    g.add_node("write_report", write_report)
    g.add_edge(START, "categorise")
    g.add_edge("categorise", "analyse")
    g.add_edge("analyse", "write_report")
    g.add_edge("write_report", END)
    return g.compile()


def main() -> None:
    p = argparse.ArgumentParser(description="LangGraph bank statement analyst (synthetic data)")
    p.add_argument("csv", nargs="?", default=str(SAMPLE), help="CSV with columns date, description, amount")
    a = p.parse_args()
    path = Path(a.csv)
    if path == SAMPLE and not SAMPLE.exists():
        make_sample(SAMPLE)
    if not path.is_file():
        print(f"File not found: {path}")
        sys.exit(1)
    rows = load(path)
    if not rows:
        print("The statement has no transactions.")
        sys.exit(1)
    out = build_graph().invoke({"rows": rows, "findings": {}, "report": ""})
    print(f"\n===== REPORT =====\n{out['report']}\n\nEducational tool only; not financial advice.")


if __name__ == "__main__":
    main()
