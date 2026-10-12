# Agent 07 - Shopping Partner (Agno)

## What it does
Describe what you want to buy ("noise cancelling headphones under 200 dollars"). The agent searches the store's catalog (`catalog.json`), recommends up to 3 products in a table, and names a top pick with one trade-off.

## Concepts you learn
- **Plain Python functions as tools:** `search_products` and `get_product` are ordinary functions. Agno reads their type hints and docstrings (including the `Args:` section) to build the tool schema the model sees.
- **Turning a sentence into parameters:** the model converts "under 200 dollars" into `max_price=200` and "noise cancelling" into `must_have`.
- **Grounding in your own data:** "never invent products" plus a real catalog stops the model recommending items you don't sell.

## The flow
```
request -> model -> search_products(category, max_price, must_have) -> JSON results -> table + top pick
```

## Run
```
cd 50-agents-for-all
.venv-agno\Scripts\python.exe 01_agno\07_shopping_partner\main.py "noise cancelling headphones under 200 dollars"
```
Empty request prints a message and exits with code 1.

## Things to try
- Ask for something with no match ("a laptop under 300") and see it suggest relaxing a filter.
- Add products or a new category to `catalog.json`.
- Add a third tool, for example `compare_products(id_a, id_b)`.

## Known limits
- Category matching is simple (exact name, plural allowed).
- The model sometimes adds generic advice outside the catalog in the trade-off text.
