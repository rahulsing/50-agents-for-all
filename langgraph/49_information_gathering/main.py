import sys
import uuid
from pathlib import Path
from typing import Literal

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import AIMessage, ToolMessage
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from pydantic import BaseModel, Field

from common.llm import DEFAULT_MODEL, OLLAMA_URL

llm = ChatOllama(model=DEFAULT_MODEL, base_url=OLLAMA_URL, temperature=0)


class PromptInstructions(BaseModel):
    """Call this ONLY when you know all four: objective, variables, constraints and requirements."""
    objective: str = Field(description="What the prompt should achieve")
    variables: list[str] = Field(description="Inputs that will be filled into the prompt")
    constraints: list[str] = Field(description="Things the output must avoid")
    requirements: list[str] = Field(description="Things the output must do, e.g. format")


GATHER = """You help the user design a prompt template for an LLM. Ask questions, one or two at a time, until you know:
1. the objective, 2. the variables passed in, 3. constraints (what to avoid), 4. requirements (format, tone).
Do not guess missing items; ask. When you know all four, call PromptInstructions."""


def gather(state: MessagesState) -> dict:
    return {"messages": [llm.bind_tools([PromptInstructions]).invoke([("system", GATHER)] + state["messages"])]}


def route(state: MessagesState) -> Literal["write_prompt", "__end__"]:
    last = state["messages"][-1]
    return "write_prompt" if isinstance(last, AIMessage) and last.tool_calls else END  # END = wait for the user


def write_prompt(state: MessagesState) -> dict:
    call = state["messages"][-1].tool_calls[0]
    spec = PromptInstructions(**call["args"])
    print(f"\n[collected] {spec.model_dump()}")
    template = llm.invoke(
        "Write a reusable prompt template from this spec. Put each variable in {curly_braces}.\n"
        f"{spec.model_dump_json(indent=2)}").content
    return {"messages": [ToolMessage(content="Spec complete.", tool_call_id=call["id"]),
                         AIMessage(content=f"Here is your prompt template:\n\n{template}")]}


def build_graph():
    g = StateGraph(MessagesState)
    g.add_node("gather", gather)
    g.add_node("write_prompt", write_prompt)
    g.add_edge(START, "gather")
    g.add_conditional_edges("gather", route)
    g.add_edge("write_prompt", END)
    return g.compile(checkpointer=InMemorySaver())  # remembers the conversation between turns


def main() -> None:
    graph = build_graph()
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    print("Prompt-template designer. Tell me what you want the prompt to do. Type 'exit' to quit.")
    while True:
        try:
            text = input("\nyou> ").strip()
        except EOFError:
            break
        if text.lower() in {"exit", "quit"}:
            break
        if not text:
            continue
        out = graph.invoke({"messages": [("user", text)]}, config)
        print(f"\nbot> {out['messages'][-1].content}")
        if out["messages"][-1].content.startswith("Here is your prompt template"):
            break


if __name__ == "__main__":
    main()
