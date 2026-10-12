"""A2A client: a LangGraph planner that discovers the research agent (56) by its agent card and delegates to it."""
import asyncio
import operator
import sys
from pathlib import Path
from typing import Annotated, TypedDict

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import httpx
from a2a.client import ClientConfig, create_client
from a2a.helpers.proto_helpers import get_stream_response_text, new_text_message
from a2a.types import Role, SendMessageRequest
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from common.llm import DEFAULT_MODEL, OLLAMA_URL

SERVER = "http://localhost:9999"
llm = ChatOllama(model=DEFAULT_MODEL, base_url=OLLAMA_URL, temperature=0)


class Questions(BaseModel):
    questions: list[str] = Field(description="2 short factual research questions")


class State(TypedDict):
    goal: str
    questions: list[str]
    answers: Annotated[list[str], operator.add]
    report: str


async def ask_remote_agent(question: str) -> str:
    """Send one question to the remote A2A agent and collect its text reply."""
    # The remote agent searches the web and runs a local LLM, which takes longer than httpx's default timeout
    config = ClientConfig(httpx_client=httpx.AsyncClient(timeout=300))
    client = await create_client(SERVER, client_config=config)  # reads the agent card, picks a transport
    request = SendMessageRequest(message=new_text_message(question, role=Role.ROLE_USER))
    parts = [get_stream_response_text(r) async for r in client.send_message(request)]
    await client.close()
    return "\n".join(p for p in parts if p)


def plan(state: State) -> dict:
    q = llm.with_structured_output(Questions).invoke(f"Goal: {state['goal']}\nWhat 2 facts do we need to look up?")
    # In testing the model sometimes returned an empty list, so the planner skipped the remote agent entirely
    # and answered from memory. Falling back to the goal itself guarantees at least one A2A call.
    questions = [x for x in q.questions if x.strip()][:2] or [state["goal"]]
    print("[planner] questions:", questions)
    return {"questions": questions}


async def delegate(state: State) -> dict:
    answers = []
    for question in state["questions"]:
        print(f"\n[planner -> research agent via A2A] {question}")
        reply = await ask_remote_agent(question)
        print(f"[research agent] {reply[:400]}")
        answers.append(f"Q: {question}\nA: {reply}")
    return {"answers": answers}


def write(state: State) -> dict:
    report = llm.invoke(f"Goal: {state['goal']}\nResearch from a partner agent:\n" + "\n\n".join(state["answers"])
                        + "\n\nWrite a short, clear answer to the goal (under 150 words) and keep the source URLs.")
    return {"report": report.content}


def build_graph():
    g = StateGraph(State)
    g.add_node("plan", plan)
    g.add_node("delegate", delegate)
    g.add_node("write", write)
    g.add_edge(START, "plan")
    g.add_edge("plan", "delegate")
    g.add_edge("delegate", "write")
    g.add_edge("write", END)
    return g.compile()


async def run(goal: str) -> None:
    async with httpx.AsyncClient() as http:  # show discovery: read the remote agent's card first
        card = (await http.get(f"{SERVER}/.well-known/agent-card.json", timeout=5)).json()
    print(f"Discovered agent: {card['name']} - skills: {[s['name'] for s in card.get('skills', [])]}\n")
    out = await build_graph().ainvoke({"goal": goal, "questions": [], "answers": [], "report": ""})
    print(f"\n===== FINAL =====\n{out['report']}")


def main() -> None:
    goal = " ".join(sys.argv[1:]).strip()
    if not goal:
        print('Please give a goal, e.g. main.py "Should I visit Iceland in winter or summer?"')
        sys.exit(1)
    try:
        asyncio.run(run(goal))
    except httpx.ConnectError:
        print(f"Cannot reach the A2A server at {SERVER}. Start it first:\n"
              r"  .venv-agno\Scripts\python.exe 07_protocols\56_research_a2a_server\server.py")
        sys.exit(1)


if __name__ == "__main__":
    main()
