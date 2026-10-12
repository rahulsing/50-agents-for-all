"""A2A server: exposes the Agno research agent (agent 01) so that other agents can discover and call it."""
import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import uvicorn
from a2a.helpers.proto_helpers import new_text_message
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes.agent_card_routes import create_agent_card_routes
from a2a.server.routes.jsonrpc_routes import create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill
from a2a.utils import DEFAULT_RPC_URL, TransportProtocol
from agno.agent import Agent
from agno.models.ollama import Ollama
from starlette.applications import Starlette

from common.llm import DEFAULT_MODEL, OLLAMA_URL
from common.tools import web_search


def build_agent() -> Agent:
    return Agent(
        model=Ollama(id=DEFAULT_MODEL, host=OLLAMA_URL),
        tools=[web_search],
        instructions=["Search the web before answering.", "Answer in 5 bullet points.",
                      "End with a 'Sources:' list of full URLs."],
    )


class ResearchExecutor(AgentExecutor):
    """Bridges A2A requests to the Agno agent: read the incoming text, run the agent, send back a message."""

    def __init__(self):
        self.agent = build_agent()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        question = context.get_user_input()
        print(f"[a2a] received: {question!r}")
        result = await asyncio.to_thread(self.agent.run, question)  # Agno's run() is blocking
        await event_queue.enqueue_event(
            new_text_message(str(result.content), context_id=context.context_id, task_id=context.task_id))
        print("[a2a] answered")

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError("cancel is not supported")


def agent_card(port: int) -> AgentCard:
    """The agent card is the public 'business card' other agents download to learn what this agent can do."""
    return AgentCard(
        name="Local Research Agent",
        description="Searches the web and answers questions in 5 cited bullet points. Runs on local Ollama.",
        version="1.0.0",
        supported_interfaces=[AgentInterface(url=f"http://localhost:{port}{DEFAULT_RPC_URL}",
                                             protocol_binding=TransportProtocol.JSONRPC.value)],
        capabilities=AgentCapabilities(streaming=False),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        skills=[AgentSkill(id="web_research", name="Web research",
                           description="Answer a factual question using a web search, with sources.",
                           tags=["research", "search", "facts"],
                           examples=["What is retrieval augmented generation?", "Who won the last World Cup?"])],
    )


def build_app(port: int) -> Starlette:
    card = agent_card(port)
    handler = DefaultRequestHandler(agent_executor=ResearchExecutor(), task_store=InMemoryTaskStore(),
                                    agent_card=card)
    return Starlette(routes=create_agent_card_routes(card) + create_jsonrpc_routes(handler, DEFAULT_RPC_URL))


def main() -> None:
    p = argparse.ArgumentParser(description="A2A server for the research agent")
    p.add_argument("--port", type=int, default=9999)
    a = p.parse_args()
    print(f"Agent card: http://localhost:{a.port}/.well-known/agent-card.json")
    uvicorn.run(build_app(a.port), host="127.0.0.1", port=a.port, log_level="warning")


if __name__ == "__main__":
    main()
