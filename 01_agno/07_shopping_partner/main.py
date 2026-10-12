import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agno.agent import Agent
from agno.models.ollama import Ollama

from common.llm import DEFAULT_MODEL, OLLAMA_URL

CATALOG = json.loads((Path(__file__).parent / "catalog.json").read_text(encoding="utf-8"))


def search_products(category: str, max_price: float = 100000, must_have: str = "") -> str:
    """Search the store catalog.

    Args:
        category: product category: headphones, laptop or kettle
        max_price: highest price in USD the user accepts
        must_have: optional feature that must appear, e.g. 'noise cancelling'
    """
    cat = category.lower().strip()
    hits = [
        p for p in CATALOG
        if p["category"] in (cat, cat.rstrip("s"))
        and p["price"] <= float(max_price)
        and (not must_have or any(must_have.lower() in f for f in p["features"]))
    ]
    return json.dumps(hits) if hits else "No products match."


def get_product(product_id: str) -> str:
    """Get full details of one product by its id, e.g. H1."""
    for p in CATALOG:
        if p["id"] == product_id.upper():
            return json.dumps(p)
    return "Unknown product id."


def build_agent() -> Agent:
    return Agent(
        model=Ollama(id=DEFAULT_MODEL, host=OLLAMA_URL),
        tools=[search_products, get_product],  # plain functions: Agno builds each tool schema from the docstring
        instructions=[
            "You are a shopping assistant for this store only. Use search_products; never invent products.",
            "Recommend at most 3 products in a markdown table (name, price, rating, why it fits).",
            "Then name your single top pick and one trade-off. If nothing fits, say so and suggest relaxing a filter.",
        ],
        markdown=True,
        debug_mode=True,
    )


def main() -> None:
    request = " ".join(sys.argv[1:]).strip()
    if not request:
        print('Please describe what you want, e.g. main.py "noise cancelling headphones under 200 dollars"')
        sys.exit(1)
    build_agent().print_response(request)


if __name__ == "__main__":
    main()
