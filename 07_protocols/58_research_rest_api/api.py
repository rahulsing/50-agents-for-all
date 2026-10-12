"""REST API: the research agent (agent 01) behind HTTP endpoints, so any app or script can call it."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import uvicorn
from agno.agent import Agent
from agno.models.ollama import Ollama
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from common.llm import DEFAULT_MODEL, OLLAMA_URL
from common.tools import web_search

app = FastAPI(title="Local Research Agent API", version="1.0.0",
              description="Ask questions; the agent searches the web and answers with sources.")


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500, examples=["What is retrieval augmented generation?"])


class AskResponse(BaseModel):
    answer: str
    model: str
    tools_used: list[str]


def build_agent() -> Agent:
    # A new agent per request keeps requests independent (no shared conversation history)
    return Agent(model=Ollama(id=DEFAULT_MODEL, host=OLLAMA_URL), tools=[web_search],
                 instructions=["Search the web before answering.", "Answer in 5 bullet points.",
                               "End with a 'Sources:' list of full URLs."])


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model": DEFAULT_MODEL}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    """Run the agent and return the full answer as JSON (FastAPI runs this in a worker thread)."""
    try:
        run = build_agent().run(req.question)
    except Exception as e:  # noqa: BLE001 - surface model/network errors as HTTP 502
        raise HTTPException(status_code=502, detail=f"Agent failed: {e}") from e
    tools = [t.tool_name for t in (run.tools or [])]
    return AskResponse(answer=str(run.content), model=DEFAULT_MODEL, tools_used=tools)


@app.post("/ask/stream")
def ask_stream(req: AskRequest) -> StreamingResponse:
    """Stream the answer as Server-Sent Events, token by token, like a chat UI.

    Each event's data is a JSON string, because raw newlines are not allowed inside an SSE data line."""
    def events():
        for chunk in build_agent().run(req.question, stream=True):
            text = getattr(chunk, "content", None)
            if isinstance(text, str) and text:
                yield f"data: {json.dumps(text)}\n\n"
        yield "event: done\ndata: \"[DONE]\"\n\n"
    return StreamingResponse(events(), media_type="text/event-stream")


def main() -> None:
    p = argparse.ArgumentParser(description="Serve the research agent over HTTP")
    p.add_argument("--port", type=int, default=8000)
    a = p.parse_args()
    print(f"API docs: http://localhost:{a.port}/docs")
    uvicorn.run(app, host="127.0.0.1", port=a.port, log_level="warning")


if __name__ == "__main__":
    main()
