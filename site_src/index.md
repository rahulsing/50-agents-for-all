# 58 AI Agents on Your Own Computer

**Learn how AI agents work by reading and running 58 small, complete examples, all on free local models with [Ollama](https://ollama.com). No API keys, no cloud bills.**

Each agent is one short Python file plus a README that explains the idea behind it: what it does, the concepts it teaches, how the code flows, how to run it, things to try, and its honest limits.

<div class="grid cards" markdown>

-   **58 agents**

    50 core agents across five frameworks, plus 8 extras: the plain Anthropic SDK, MCP, A2A, a REST API, a bank-statement analyst and a stock-portfolio watcher.

-   **5 frameworks, side by side**

    LangGraph (14), CrewAI (12), Agno (10), AutoGen (9) and LlamaIndex (5). Several ideas are built in more than one framework, so you can compare them.

-   **Runs locally**

    Every agent was run and checked on a 7B model (`qwen2.5:7b-instruct`) through Ollama. Your data never leaves your machine.

-   **Honest about failure**

    Small models make mistakes. Each README records what went wrong in testing and how the code was changed to fix it. Those lessons are the most valuable part.

</div>

## Where to start

1. **[Getting started](getting-started.md)**: install Ollama and Python, and run your first agent in about 10 minutes.
2. **[How to read an agent](how-to-read.md)**: how every page is organised and a suggested learning path.
3. Pick a framework from the menu, or browse the **[full agent index](agent-index.md)**.
4. Read **[Lessons learned](lessons.md)** to see how to make small local models reliable.

## What an agent looks like

Agent 01 asks a question, searches the web, and answers with sources. Here is its real output:

![Agent 01 output](assets/agent01_result.png)

## A suggested path through the 58 agents

| Step | Read these | You will understand |
|------|------------|---------------------|
| 1. One agent, one tool | [01 Research Agent](agents/agno/01_research_agent.md), [51 same agent with the plain Anthropic SDK](agents/anthropic_sdk/51_research_agent.md) | What "tool calling" is, and the loop every framework hides from you |
| 2. Your own documents (RAG) | [05 Document Q&A](agents/llamaindex/05_document_qa.md), [02 Agentic RAG](agents/langgraph/02_agentic_rag.md), [13 Corrective RAG](agents/langgraph/13_corrective_rag.md) | Retrieval, embeddings, grading retrieved text |
| 3. Teams of agents | [03 Trip Planner](agents/crewai/03_trip_planner.md), [19 Group Chat](agents/autogen/19_group_chat.md), [31 Supervisor](agents/langgraph/31_supervisor_multi_agent.md) | Roles, hand-offs, supervisors |
| 4. Structured output | [07 Recipe Creator](agents/agno/07_recipe_creator.md), [18 Marketing Strategy](agents/crewai/18_marketing_strategy.md) | Getting validated objects instead of free text |
| 5. Self-improvement | [08 Reflection](agents/langgraph/08_reflection_agent.md), [17 Self-RAG](agents/langgraph/17_self_rag.md), [35 Reflexion](agents/langgraph/35_reflexion_agent.md) | Agents that critique and fix their own work |
| 6. Humans and safety | [38 Customer Support](agents/langgraph/38_customer_support.md), [Guardrails](guardrails.md) | Human approval, guardrails, keeping actions in code |
| 7. Connecting agents | [52 MCP](agents/protocols/52_notes_mcp_agno.md), [54 A2A server](agents/protocols/54_research_a2a_server.md), [56 REST API](agents/protocols/56_research_rest_api.md) | Standard protocols for tools, agents and apps |

!!! note "About the code"
    The agent ideas come from the community list [500 AI Agents Projects](https://github.com/ashishpatel26/500-AI-Agents-Projects). All code here is original, written for local models. Sample data (companies, people, orders, contracts) is fictional.
