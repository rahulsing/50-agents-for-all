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
| 1. One agent, one tool | [01 Research Agent](agents/01_agno/01_research_agent.md), [53 same agent with the plain Anthropic SDK](agents/06_anthropic_sdk/53_research_agent.md) | What "tool calling" is, and the loop every framework hides from you |
| 2. Your own documents (RAG) | [48 Document Q&A](agents/05_llamaindex/48_document_qa.md), [11 Agentic RAG](agents/02_langgraph/11_agentic_rag.md), [13 Corrective RAG](agents/02_langgraph/13_corrective_rag.md) | Retrieval, embeddings, grading retrieved text |
| 3. Teams of agents | [26 Trip Planner](agents/03_crewai/26_trip_planner.md), [41 Group Chat](agents/04_autogen/41_group_chat.md), [18 Supervisor](agents/02_langgraph/18_supervisor_multi_agent.md) | Roles, hand-offs, supervisors |
| 4. Structured output | [03 Recipe Creator](agents/01_agno/03_recipe_creator.md), [29 Marketing Strategy](agents/03_crewai/29_marketing_strategy.md) | Getting validated objects instead of free text |
| 5. Self-improvement | [12 Reflection](agents/02_langgraph/12_reflection_agent.md), [14 Self-RAG](agents/02_langgraph/14_self_rag.md), [19 Reflexion](agents/02_langgraph/19_reflexion_agent.md) | Agents that critique and fix their own work |
| 6. Humans and safety | [20 Customer Support](agents/02_langgraph/20_customer_support.md), [Guardrails](guardrails.md) | Human approval, guardrails, keeping actions in code |
| 7. Connecting agents | [54 MCP](agents/07_protocols/54_notes_mcp_agno.md), [56 A2A server](agents/07_protocols/56_research_a2a_server.md), [58 REST API](agents/07_protocols/58_research_rest_api.md) | Standard protocols for tools, agents and apps |

!!! note "About the code"
    The agent ideas come from the community list [500 AI Agents Projects](https://github.com/ashishpatel26/500-AI-Agents-Projects). All code here is original, written for local models. Sample data (companies, people, orders, contracts) is fictional.
