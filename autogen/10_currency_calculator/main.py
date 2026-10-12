import asyncio
import sys
from pathlib import Path
from typing import Annotated

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import httpx
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console

from common.autogen_client import ollama_client
from common.llm import DEFAULT_MODEL

# Fallback rates (USD base) used when the free rates API cannot be reached
FALLBACK = {"USD": 1.0, "EUR": 0.92, "GBP": 0.79, "INR": 83.5, "JPY": 151.0, "CAD": 1.36, "AUD": 1.52, "CHF": 0.88}


def get_rate(base: str, target: str) -> tuple[float, str]:
    base, target = base.upper(), target.upper()
    try:  # Frankfurter: free, no API key, European Central Bank rates
        r = httpx.get("https://api.frankfurter.dev/v1/latest", params={"base": base, "symbols": target}, timeout=10)
        r.raise_for_status()
        data = r.json()
        return float(data["rates"][target]), f"ECB rate on {data['date']}"
    except Exception:  # noqa: BLE001 - offline or unknown currency: fall back to the table
        if base in FALLBACK and target in FALLBACK:
            return FALLBACK[target] / FALLBACK[base], "offline fallback table (approximate)"
        raise ValueError(f"Unknown currency pair {base}/{target}")


def convert_currency(amount: Annotated[float, "Amount of money to convert"],
                     from_currency: Annotated[str, "3-letter code, e.g. USD"],
                     to_currency: Annotated[str, "3-letter code, e.g. EUR"]) -> str:
    """Convert an amount between two currencies using the latest exchange rate."""
    try:
        rate, source = get_rate(from_currency, to_currency)
    except ValueError as e:
        return str(e)
    return f"{amount:,.2f} {from_currency.upper()} = {amount * rate:,.2f} {to_currency.upper()} " \
           f"(rate {rate:.4f}, {source})"


async def run(question: str) -> None:
    client = ollama_client(DEFAULT_MODEL)
    agent = AssistantAgent(
        "currency_agent",
        model_client=client,
        tools=[convert_currency],  # AutoGen turns the type hints + docstring into a tool schema
        reflect_on_tool_use=True,  # after the tool runs, the model writes a natural-language answer
        system_message="You convert currencies. Always use convert_currency; never guess rates. "
                       "For several conversions, call the tool once per pair.",
    )
    await Console(agent.run_stream(task=question))
    await client.close()


def main() -> None:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        print('Please ask a question, e.g. main.py "How much is 250 USD in EUR and in INR?"')
        sys.exit(1)
    asyncio.run(run(question))


if __name__ == "__main__":
    main()
