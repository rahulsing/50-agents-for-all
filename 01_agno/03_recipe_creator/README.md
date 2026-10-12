# Agent 03 - Recipe Creator (Agno)

## What it does
List the ingredients you have (and optionally a diet). It returns one recipe with servings, time, ingredient quantities and numbered steps.

## Concepts you learn
- **Structured output:** `output_schema=Recipe` makes the agent return a validated Pydantic object instead of free text. Your code then reads `recipe.steps`, `recipe.servings` and so on, which is how agents feed other programs.
- **Field descriptions guide the model:** the `Field(description=...)` text in the schema is sent to the model and tells it what each field means.
- **No tools needed:** not every agent needs tools; this one is model + instructions + schema.

## The flow
```
ingredients + diet -> model (forced to fill the Recipe schema) -> Recipe object -> formatted printout
```

## Run
```
cd 50-agents-for-all
.venv-agno\Scripts\python.exe 01_agno\03_recipe_creator\main.py "eggs, spinach, feta, bread" --diet vegetarian
```
Empty ingredients print a message and exit with code 1; an invalid model reply exits with code 2.

## Things to try
- Add a field to `Recipe`, for example `calories_per_serving: int`, and print it.
- Try `--diet vegan` with ingredients that include eggs and see how it adapts.
- Print `run.content.model_dump_json(indent=2)` to see the raw structured result.

## Known limits
- The model checks its own `uses_only_given` flag and can be wrong (it said True while adding milk).
- Times and quantities are estimates; a 7B model can be inconsistent (for example total time shorter than the bake time).
