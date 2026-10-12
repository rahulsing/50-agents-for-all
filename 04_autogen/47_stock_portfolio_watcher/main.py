import argparse
import asyncio
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import yfinance as yf
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console

from common.autogen_client import ollama_client
from common.llm import DEFAULT_MODEL

DEFAULT_PORTFOLIO = Path(__file__).parent / "portfolio.csv"
PORTFOLIO_FILE = DEFAULT_PORTFOLIO


def _closes(ticker: str, period: str = "6mo"):
    return yf.Ticker(ticker).history(period=period)["Close"]


def portfolio_snapshot() -> str:
    """Current value, profit/loss and weight of every holding in the portfolio, plus the total."""
    with open(PORTFOLIO_FILE, encoding="utf-8") as f:
        holdings = list(csv.DictReader(f))
    priced, missing = [], []
    for h in holdings:
        closes = _closes(h["ticker"], "5d")
        if closes.empty:
            missing.append(h["ticker"])
            continue
        shares, cost = float(h["shares"]), float(h["buy_price"])
        price = float(closes.iloc[-1])
        priced.append({"ticker": h["ticker"], "price": price, "value": price * shares,
                       "cost": cost * shares, "pl": (price - cost) * shares})
    total_value = sum(p["value"] for p in priced)
    total_cost = sum(p["cost"] for p in priced)
    lines = [f"{p['ticker']}: price {p['price']:.2f}, value {p['value']:,.2f}, P/L {p['pl']:+,.2f} "
             f"({p['pl'] / p['cost'] * 100:+.1f}%), weight {p['value'] / total_value * 100:.1f}%" for p in priced]
    lines += [f"{t}: no price data" for t in missing]
    return "\n".join(lines) + f"\nTOTAL value {total_value:,.2f}, P/L {total_value - total_cost:+,.2f}"


def technical_indicators(ticker: str) -> str:
    """20/50-day moving averages, 14-day RSI and 1-month price change for one ticker."""
    c = _closes(ticker.upper())
    if len(c) < 50:
        return f"Not enough price history for {ticker}"
    delta = c.diff()
    gain, loss = delta.clip(lower=0).rolling(14).mean(), (-delta.clip(upper=0)).rolling(14).mean()
    rsi = float(100 - 100 / (1 + gain.iloc[-1] / loss.iloc[-1])) if loss.iloc[-1] else 100.0
    sma20, sma50, last = float(c.rolling(20).mean().iloc[-1]), float(c.rolling(50).mean().iloc[-1]), float(c.iloc[-1])
    change = (last / float(c.iloc[-22]) - 1) * 100
    trend = "above" if last > sma50 else "below"
    return (f"{ticker.upper()}: last {last:.2f}, SMA20 {sma20:.2f}, SMA50 {sma50:.2f} (price {trend} SMA50), "
            f"RSI14 {rsi:.0f}, 1-month change {change:+.1f}%")


async def run() -> None:
    client = ollama_client(DEFAULT_MODEL)
    analyst = AssistantAgent(
        "portfolio_analyst", model_client=client, tools=[portfolio_snapshot, technical_indicators],
        max_tool_iterations=8, reflect_on_tool_use=True,
        system_message="Call portfolio_snapshot, then technical_indicators for EVERY ticker in it. Then write: "
                       "a holdings table, total value and P/L, and one line per stock on its trend "
                       "(RSI > 70 = overbought, < 30 = oversold). Use only tool numbers.")
    risk = AssistantAgent(
        "risk_reviewer", model_client=client,
        system_message="Review the analyst's report for risk: concentration (any holding > 35% weight), "
                       "overbought/oversold stocks, and big losers. Give 3 bullet points to watch. "
                       "End with: 'Educational use only, not financial advice.'")
    team = RoundRobinGroupChat([analyst, risk], termination_condition=MaxMessageTermination(3))
    await Console(team.run_stream(task="Review my stock portfolio."))
    await client.close()


def main() -> None:
    global PORTFOLIO_FILE
    p = argparse.ArgumentParser(description="AutoGen stock portfolio watcher")
    p.add_argument("portfolio", nargs="?", default=str(DEFAULT_PORTFOLIO), help="CSV: ticker,shares,buy_price")
    a = p.parse_args()
    PORTFOLIO_FILE = Path(a.portfolio)
    if not PORTFOLIO_FILE.is_file():
        print(f"Portfolio file not found: {PORTFOLIO_FILE}")
        sys.exit(1)
    asyncio.run(run())


if __name__ == "__main__":
    main()
