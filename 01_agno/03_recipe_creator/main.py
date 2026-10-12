import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agno.agent import Agent
from agno.models.ollama import Ollama
from pydantic import BaseModel, Field

from common.llm import DEFAULT_MODEL, OLLAMA_URL


class Recipe(BaseModel):
    name: str
    servings: int
    prep_minutes: int = Field(description="Total time in minutes")
    ingredients: list[str] = Field(description="Each item with a quantity, e.g. '2 eggs'")
    steps: list[str]
    uses_only_given: bool = Field(description="True if no main ingredients beyond the given ones (pantry staples allowed)")


def build_agent() -> Agent:
    return Agent(
        model=Ollama(id=DEFAULT_MODEL, host=OLLAMA_URL),
        instructions=[
            "You are a home cook. Create one recipe from the ingredients the user has.",
            "You may add pantry staples: salt, pepper, oil, butter, water, flour, sugar, common spices.",
            "Respect any dietary need the user states.",
        ],
        output_schema=Recipe,
    )


def main() -> None:
    p = argparse.ArgumentParser(description="Agno recipe creator with structured output")
    p.add_argument("ingredients", nargs="?", default="")
    p.add_argument("--diet", default="none")
    a = p.parse_args()
    if not a.ingredients.strip():
        print('Please list ingredients, e.g. main.py "eggs, spinach, feta"')
        sys.exit(1)
    run = build_agent().run(f"Ingredients: {a.ingredients}\nDietary need: {a.diet}")
    r: Recipe = run.content
    if not isinstance(r, Recipe):
        print("The model did not return a valid recipe. Try again.")
        sys.exit(2)
    print(f"\n# {r.name}\nServes {r.servings} | {r.prep_minutes} min | only given ingredients: {r.uses_only_given}\n")
    print("## Ingredients")
    print("\n".join(f"- {i}" for i in r.ingredients))
    print("\n## Steps")
    print("\n".join(f"{n}. {s}" for n, s in enumerate(r.steps, 1)))


if __name__ == "__main__":
    main()
