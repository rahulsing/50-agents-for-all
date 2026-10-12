import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.yfinance import YFinanceTools

from common.llm import DEFAULT_MODEL, OLLAMA_URL


def build_agent() -> Agent:
    return Agent(
        model=Ollama(id=DEFAULT_MODEL, host=OLLAMA_URL),
        tools=[
            YFinanceTools(
                enable_stock_price=True,
                enable_company_info=True,
                enable_key_financial_ratios=True,
                enable_analyst_recommendations=True,
            )
        ],
        instructions=[
            "You are a financial data assistant. Always fetch data with your tools; never invent numbers.",
            "Use ticker symbols (Apple = AAPL, Microsoft = MSFT, etc.).",
            "Present numbers in a markdown table, then 3 bullet observations.",
            "End with: 'Educational use only, not financial advice.'",
        ],
        markdown=True,
        debug_mode=True,
    )


def main() -> None:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        print('Please provide a question, e.g. main.py "Compare AAPL and MSFT price and P/E"')
        sys.exit(1)
    build_agent().print_response(question)


if __name__ == "__main__":
    main()
