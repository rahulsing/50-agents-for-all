import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import common.crewai_env  # noqa: F401  (must come before crewai)

import yfinance as yf
from crewai import Agent, Crew, Process, Task
from crewai.tools import tool

from common.crewai_env import ollama_llm
from common.llm import DEFAULT_MODEL
from common.tools import web_search as _web_search


@tool("stock_fundamentals")
def stock_fundamentals(ticker: str) -> str:
    """Get price, valuation and growth figures for a stock ticker such as AAPL."""
    info = yf.Ticker(ticker.strip().upper()).info
    keys = ["longName", "currentPrice", "marketCap", "trailingPE", "forwardPE", "revenueGrowth", "profitMargins",
            "debtToEquity", "fiftyTwoWeekHigh", "fiftyTwoWeekLow", "recommendationKey"]
    return "\n".join(f"{k}: {info.get(k)}" for k in keys) if info.get("longName") else f"No data for {ticker}"


@tool("price_history")
def price_history(ticker: str) -> str:
    """Get monthly closing prices for the last 6 months for a ticker."""
    h = yf.Ticker(ticker.strip().upper()).history(period="6mo", interval="1mo")
    return "\n".join(f"{d.date()}: {c:.2f}" for d, c in h["Close"].items()) or f"No history for {ticker}"


@tool("web_search")
def web_search(query: str) -> str:
    """Search the web for recent news; returns titles, snippets and URLs."""
    return _web_search(query, 5)


def build_crew(ticker: str) -> Crew:
    llm = ollama_llm(DEFAULT_MODEL, temperature=0.2)
    analyst = Agent(role="Financial Data Analyst", goal=f"Explain {ticker}'s numbers accurately",
                    backstory="You only use numbers returned by your tools and never invent figures.",
                    tools=[stock_fundamentals, price_history], llm=llm, allow_delegation=False, verbose=True)
    news = Agent(role="Market News Researcher", goal=f"Find the most important recent news about {ticker}",
                 backstory="You separate facts from rumours and always give sources.",
                 tools=[web_search], llm=llm, allow_delegation=False, verbose=True)
    advisor = Agent(role="Investment Report Writer", goal="Write a balanced, plain-English stock report",
                    backstory="You present bull and bear cases fairly and never give personal advice.",
                    llm=llm, allow_delegation=False, verbose=True)

    t_numbers = Task(description=f"Use stock_fundamentals and price_history for {ticker}. Report valuation, "
                                 "growth, profitability and the 6-month trend.",
                     expected_output="A short table of key figures and 3 observations.", agent=analyst)
    t_news = Task(description=f"Search for news about {ticker} from the last few months. List the 4 most "
                              "important items with one line each and the URL.",
                  expected_output="4 news bullets with URLs.", agent=news)
    t_report = Task(description=f"Write a report on {ticker}: Summary, Key figures, Recent news, Bull case, "
                                "Bear case, Overall view (positive / neutral / negative with one reason). "
                                "End with 'Educational use only, not financial advice.'",
                    expected_output="A markdown report under 450 words.", agent=advisor,
                    context=[t_numbers, t_news])
    return Crew(agents=[analyst, news, advisor], tasks=[t_numbers, t_news, t_report], process=Process.sequential)


def main() -> None:
    ticker = " ".join(sys.argv[1:]).strip().upper()
    if not ticker or not ticker.replace(".", "").replace("-", "").isalnum() or len(ticker) > 10:
        print("Please provide a stock ticker, e.g. main.py NVDA")
        sys.exit(1)
    print(build_crew(ticker).kickoff().raw)


if __name__ == "__main__":
    main()
