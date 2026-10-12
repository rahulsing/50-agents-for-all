# How to read an agent

Every agent page follows the same structure, taken from the README in the agent's folder, followed by its complete source code.

| Section | What it tells you |
|---------|-------------------|
| **What it does** | The task in plain words |
| **Concepts you learn** | The 2-4 ideas this example exists to teach |
| **The flow / The graph / The crew** | A small diagram of how control moves through the agent |
| **How the code works** | A walk through `main.py`, step by step |
| **Run** | The exact command, including what happens on bad input |
| **Things to try** | Small changes that show the concept in action |
| **Known limits** | What went wrong in testing with a 7B model, and what the code does about it |
| **The code** | Every Python file of the agent, ready to copy |

## The five frameworks in one sentence each

| Framework | Mental model | Start with |
|-----------|--------------|------------|
| **Agno** | One agent = model + tools + instructions; batteries included (memory, knowledge, guardrails) | [01 Research Agent](agents/01_agno/01_research_agent.md) |
| **LangGraph** | You draw a graph of steps (nodes) and decisions (edges) that share a state | [11 Agentic RAG](agents/02_langgraph/11_agentic_rag.md) |
| **CrewAI** | A crew of role-played agents, each given tasks; or event-driven Flows | [26 Trip Planner](agents/03_crewai/26_trip_planner.md) |
| **AutoGen** | Agents that talk to each other in a team; the conversation is the program | [38 Code Feedback Loop](agents/04_autogen/38_code_feedback_loop.md) |
| **LlamaIndex** | A data framework: load documents, build indexes, query them | [48 Document Q&A](agents/05_llamaindex/48_document_qa.md) |

Want to see what all of them hide? Read [53: the same research agent with no framework at all](agents/06_anthropic_sdk/53_research_agent.md). The whole "agent" is a 20-line loop.

## Shared code

A few helpers are shared by many agents, in the `common/` folder: model names, a web-search tool with fallbacks, a safe calculator, and one small setup helper per framework. See [Shared code](shared-code.md).

## Reading tips

- Read the **Known limits** first. They show where small models fail and which code patterns fixed it.
- Run the agent, then try one item from **Things to try**. Changing one line teaches more than reading ten.
- Compare the same idea in two frameworks, for example SQL agents [15 (LangGraph)](agents/02_langgraph/15_sql_agent.md) and [42 (AutoGen)](agents/04_autogen/42_nl_to_sql.md), or research agents [01](agents/01_agno/01_research_agent.md), [40](agents/04_autogen/40_web_search_agent.md) and [53](agents/06_anthropic_sdk/53_research_agent.md).
