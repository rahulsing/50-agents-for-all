# Agent Index

58 local agents on Ollama: the main 50 across five frameworks, plus 8 extras (Anthropic SDK, MCP, A2A, REST API, banking and a stock portfolio). Every folder has a `main.py` (or a server file), a learning-oriented `README.md` and a `requirements.txt`. Framework folders are numbered `01_agno` to `07_protocols`, and agents are numbered 01-58 in that folder order.

Setup is described in [README.md](README.md) and the [Getting started](https://rahulsing.github.io/50-agents-for-all/getting-started/) guide; shared code lives in `common/`; each README has the exact command for that agent.

## Guardrails: where to look

Agents marked **[Guardrail]** in the table below demonstrate guardrails. In each file, search for `GUARDRAIL` to jump to the code; each README has a "Guardrails" section explaining it.

**Framework built-in guardrails**

| # | Agent | Framework feature | What it guards | Code |
|---|-------|-------------------|----------------|------|
| 10 | Support Agent | Agno `pre_hooks` / `post_hooks` with `PromptInjectionGuardrail`, `PIIDetectionGuardrail` + a custom output check | Blocks prompt injection and card/IBAN/SSN numbers before the model runs; blocks replies that leak numbers or instructions | [main.py#L27](01_agno/10_support_agent/main.py#L27), [hooks](01_agno/10_support_agent/main.py#L89) |
| 18 | Supervisor Multi-Agent | LangChain middleware: `PIIMiddleware`, `ModelCallLimitMiddleware`, `ToolCallLimitMiddleware` + a graph-entry PII node | Redacts emails and masks cards for the whole team; caps model and tool calls per worker | [main.py#L34](02_langgraph/18_supervisor_multi_agent/main.py#L34), [entry node](02_langgraph/18_supervisor_multi_agent/main.py#L137) |
| 27 | Job Posting Generator | CrewAI `Task(guardrails=[...], guardrail_max_retries=3)`: a function guardrail + a plain-English LLM guardrail | Length, biased wording, required sections, invented salary, discriminatory requirements; failures are sent back for a rewrite | [main.py#L19](03_crewai/27_job_posting_generator/main.py#L19), [task](03_crewai/27_job_posting_generator/main.py#L90) |

**Hand-written guardrails** (plain code that stops a small model's mistakes)

| # | Agent | Guardrail | Code |
|---|-------|-----------|------|
| 15, 42 | SQL agents | Database opened read-only; only SELECT queries accepted | [15](02_langgraph/15_sql_agent/main.py#L23), [42](04_autogen/42_nl_to_sql/main.py#L25) |
| 42 | Natural Language to SQL | `VerifiedApproval`: an approval counts only if its numbers appear in a real query result | [main.py#L50](04_autogen/42_nl_to_sql/main.py#L50) |
| 18, 23 | Supervisor / Collaboration | Workflow order enforced in code (the analyst must check numbers before finishing) | [18](02_langgraph/18_supervisor_multi_agent/main.py#L106), [23](02_langgraph/23_multi_agent_collaboration/main.py#L52) |
| 10 | Support Agent | The model only decides to escalate; code opens the ticket, and only with a real email | [main.py#L122](01_agno/10_support_agent/main.py#L122) |
| 30, 35 | Recruitment / Lead Score | Scores computed in code from the model's yes/no judgements | [30](03_crewai/30_recruitment_workflow/main.py#L28), [35](03_crewai/35_lead_score_flow/main.py#L28) |
| 46 | Conversational Chess | A referee in code validates every move | [main.py#L41](04_autogen/46_conversational_chess/main.py#L41) |
| 22, 38 | Code agents | Model-written code runs in a separate process with a timeout | [38](04_autogen/38_code_feedback_loop/), [22](02_langgraph/22_code_assistant/) |

## All agents

| # | Agent | Framework | Industry | What it does |
|---|-------|-----------|----------|--------------|
| 01 | [Research Agent](01_agno/01_research_agent/) | Agno | Research | Web search, then a 5-bullet answer with sources |
| 02 | [YouTube Agent](01_agno/02_youtube_agent/) | Agno | Media | Summarises a YouTube video or answers questions from its transcript |
| 03 | [Recipe Creator](01_agno/03_recipe_creator/) | Agno | Lifestyle | One recipe from your ingredients, as structured output |
| 04 | [Finance Agent](01_agno/04_finance_agent/) | Agno | Finance | Live stock data (price, ratios, analysts) explained in a table |
| 05 | [Study Partner](01_agno/05_study_partner/) | Agno | Education | Interactive tutor and quiz with saved sessions |
| 06 | [Legal Document Analysis](01_agno/06_legal_document_analysis/) | Agno | Legal | Clause-by-clause contract risk review from your side |
| 07 | [Shopping Partner](01_agno/07_shopping_partner/) | Agno | Retail | Searches a store catalog with plain-function tools |
| 08 | [Movie Recommendation](01_agno/08_movie_recommendation/) | Agno | Entertainment | Recommends from a movie list and remembers you between runs |
| 09 | [README Generator](01_agno/09_readme_generator/) | Agno | Software Dev | Reads a project folder (read-only) and writes its README |
| 10 | [Support Agent](01_agno/10_support_agent/) | Agno | Customer Service | **[Guardrail]** Knowledge-base answers; code opens tickets when the model escalates |
| 11 | [Agentic RAG](02_langgraph/11_agentic_rag/) | LangGraph | Knowledge & RAG | Decides when to search a handbook, answers with the section cited |
| 12 | [Reflection Agent](02_langgraph/12_reflection_agent/) | LangGraph | Agent Patterns | Writes, critiques and rewrites its own draft |
| 13 | [Corrective RAG](02_langgraph/13_corrective_rag/) | LangGraph | Knowledge & RAG | Grades retrieved text; falls back to web search when it is irrelevant |
| 14 | [Self-RAG](02_langgraph/14_self_rag/) | LangGraph | Knowledge & RAG | Checks its own answer for grounding and usefulness, retries |
| 15 | [SQL Agent](02_langgraph/15_sql_agent/) | LangGraph | Data & Analytics | Explores a read-only database, writes and fixes SQL |
| 16 | [Plan-and-Execute](02_langgraph/16_plan_and_execute/) | LangGraph | Agent Patterns | Plans steps, executes them with a sub-agent, re-plans |
| 17 | [Adaptive RAG](02_langgraph/17_adaptive_rag/) | LangGraph | Knowledge & RAG | Routes each question to handbook, web or a direct answer |
| 18 | [Supervisor Multi-Agent](02_langgraph/18_supervisor_multi_agent/) | LangGraph | Agent Patterns | **[Guardrail]** A supervisor routes work to researcher, analyst and writer |
| 19 | [Reflexion Agent](02_langgraph/19_reflexion_agent/) | LangGraph | Agent Patterns | Self-critique that triggers web searches, then a revised answer |
| 20 | [Customer Support](02_langgraph/20_customer_support/) | LangGraph | Customer Service | Intent routing, order tools, human approval for refunds |
| 21 | [Hierarchical Agent Teams](02_langgraph/21_hierarchical_agent_teams/) | LangGraph | Agent Patterns | A top supervisor over a research team and a writing team |
| 22 | [Code Assistant](02_langgraph/22_code_assistant/) | LangGraph | Software Dev | Structured code generation, executed and fixed until it runs |
| 23 | [Multi-Agent Collaboration](02_langgraph/23_multi_agent_collaboration/) | LangGraph | Agent Patterns | Researcher and analyst pass the baton until the analyst signs off |
| 24 | [Information Gathering](02_langgraph/24_information_gathering/) | LangGraph | Customer Service | Asks questions until it can write a prompt template |
| 25 | [Bank Statement Analyst](02_langgraph/25_bank_statement_analyst/) | LangGraph | Banking | Categorises spending, flags unusual transactions, suggests a budget (synthetic data) |
| 26 | [Trip Planner](03_crewai/26_trip_planner/) | CrewAI | Travel | Researcher, planner and budgeter crew for a city trip |
| 27 | [Job Posting Generator](03_crewai/27_job_posting_generator/) | CrewAI | HR | **[Guardrail]** Researches a company, drafts and reviews a job posting |
| 28 | [Stock Analysis](03_crewai/28_stock_analysis/) | CrewAI | Finance | Data analyst, news researcher and writer produce a stock report |
| 29 | [Marketing Strategy Generator](03_crewai/29_marketing_strategy/) | CrewAI | Marketing | Market research turned into a structured marketing plan |
| 30 | [Recruitment Workflow](03_crewai/30_recruitment_workflow/) | CrewAI | HR | Evidence-based CV screening, interview questions, shortlist |
| 31 | [Email Auto Responder](03_crewai/31_email_auto_responder/) | CrewAI | Customer Service | A Flow that triages an inbox, alerts on urgent mail, drafts replies |
| 32 | [Meeting Prep](03_crewai/32_meeting_prep/) | CrewAI | Business Productivity | Company and industry research into a one-page briefing |
| 33 | [Instagram Post Generator](03_crewai/33_instagram_post_generator/) | CrewAI | Marketing | Hierarchical crew with an auto-created manager |
| 34 | [Landing Page Generator](03_crewai/34_landing_page_generator/) | CrewAI | Marketing | Analyst, copywriter and coder build a single-file HTML page |
| 35 | [Lead Score Flow](03_crewai/35_lead_score_flow/) | CrewAI | Sales | A Flow that BANT-scores leads and emails the hot ones |
| 36 | [Screenplay Writer](03_crewai/36_screenplay_writer/) | CrewAI | Entertainment | Turns a forum thread into a screenplay scene |
| 37 | [Markdown Validator](03_crewai/37_markdown_validator/) | CrewAI | Software Dev | Code lints Markdown; the agent explains and fixes it |
| 38 | [Code Exec Feedback Loop](04_autogen/38_code_feedback_loop/) | AutoGen | Software Dev | Coder writes Python, executor runs it, errors feed back |
| 39 | [Currency Calculator](04_autogen/39_currency_calculator/) | AutoGen | Finance | Function calling with live ECB exchange rates |
| 40 | [Web Search Agent](04_autogen/40_web_search_agent/) | AutoGen | Research | Searches, reads pages, answers with sources |
| 41 | [Group Chat](04_autogen/41_group_chat/) | AutoGen | Agent Patterns | An LLM manager picks who speaks next among planner, researcher, writer |
| 42 | [Natural Language to SQL](04_autogen/42_nl_to_sql/) | AutoGen | Data & Analytics | **[Guardrail]** SQL writer plus a reviewer agent that approves the query |
| 43 | [RAG Group Chat](04_autogen/43_rag_group_chat/) | AutoGen | Knowledge & RAG | Retriever, answerer and checker agents with a tiny vector store |
| 44 | [Nested Chats](04_autogen/44_nested_chats/) | AutoGen | Agent Patterns | A whole review team used as one tool of a writer agent |
| 45 | [Society of Mind](04_autogen/45_society_of_mind/) | AutoGen | Agent Patterns | An inner writer/editor team acting as one agent |
| 46 | [Conversational Chess](04_autogen/46_conversational_chess/) | AutoGen | Gaming | Two LLM players; tools enforce legal moves |
| 47 | [Stock Portfolio Watcher](04_autogen/47_stock_portfolio_watcher/) | AutoGen | Finance | Portfolio value, P/L and indicators, then a risk review (not financial advice) |
| 48 | [Document Q&A](05_llamaindex/48_document_qa/) | LlamaIndex | Knowledge & RAG | Questions over a folder of your own documents, with sources |
| 49 | [CSV / SQL Query](05_llamaindex/49_csv_sql_query/) | LlamaIndex | Data & Analytics | Natural-language questions over a CSV via text-to-SQL |
| 50 | [Multi-Document Agent](05_llamaindex/50_multi_document_agent/) | LlamaIndex | Knowledge & RAG | An agent with facts and summary tools per document (city guides) |
| 51 | [Sub-Question Query Engine](05_llamaindex/51_sub_question_query_engine/) | LlamaIndex | Knowledge & RAG | Splits a comparison into per-document sub-questions |
| 52 | [Report Summarizer](05_llamaindex/52_report_summarizer/) | LlamaIndex | Knowledge & RAG | Tree-summarises a long report into summary, numbers, risks |
| 53 | [Research Agent (plain SDK)](06_anthropic_sdk/53_research_agent/) | Anthropic SDK | Research | Agent 01 rebuilt with the Anthropic SDK pointed at Ollama, hand-written tool loop |
| 54 | [Notes MCP: Agno client](07_protocols/54_notes_mcp_agno/) | Agno + MCP | Protocols | Agent uses tools from a local MCP server ([notes_mcp_server.py](07_protocols/notes_mcp_server.py)) |
| 55 | [Notes MCP: LangGraph client](07_protocols/55_notes_mcp_langgraph/) | LangGraph + MCP | Protocols | The same MCP server used from a second framework |
| 56 | [Research Agent as A2A Server](07_protocols/56_research_a2a_server/) | Agno + A2A | Protocols | Publishes an agent card and answers A2A requests |
| 57 | [Planner as A2A Client](07_protocols/57_planner_a2a_client/) | LangGraph + A2A | Protocols | Discovers agent 56 and delegates research to it |
| 58 | [Research Agent REST API](07_protocols/58_research_rest_api/) | Agno + FastAPI | Protocols | `/ask` (JSON) and `/ask/stream` (SSE) endpoints |

## By framework folder

**`01_agno/` Agno (01-10):** 01 Research Agent, 02 YouTube Agent, 03 Recipe Creator, 04 Finance Agent, 05 Study Partner, 06 Legal Document Analysis, 07 Shopping Partner, 08 Movie Recommendation, 09 README Generator, 10 Support Agent

**`02_langgraph/` LangGraph (11-25):** 11 Agentic RAG, 12 Reflection Agent, 13 Corrective RAG, 14 Self-RAG, 15 SQL Agent, 16 Plan-and-Execute, 17 Adaptive RAG, 18 Supervisor Multi-Agent, 19 Reflexion Agent, 20 Customer Support, 21 Hierarchical Agent Teams, 22 Code Assistant, 23 Multi-Agent Collaboration, 24 Information Gathering, 25 Bank Statement Analyst

**`03_crewai/` CrewAI (26-37):** 26 Trip Planner, 27 Job Posting Generator, 28 Stock Analysis, 29 Marketing Strategy Generator, 30 Recruitment Workflow, 31 Email Auto Responder, 32 Meeting Prep, 33 Instagram Post Generator, 34 Landing Page Generator, 35 Lead Score Flow, 36 Screenplay Writer, 37 Markdown Validator

**`04_autogen/` AutoGen (38-47):** 38 Code Exec Feedback Loop, 39 Currency Calculator, 40 Web Search Agent, 41 Group Chat, 42 Natural Language to SQL, 43 RAG Group Chat, 44 Nested Chats, 45 Society of Mind, 46 Conversational Chess, 47 Stock Portfolio Watcher

**`05_llamaindex/` LlamaIndex (48-52):** 48 Document Q&A, 49 CSV / SQL Query, 50 Multi-Document Agent, 51 Sub-Question Query Engine, 52 Report Summarizer

**`06_anthropic_sdk/` Anthropic SDK (no framework) (53):** 53 Research Agent (plain SDK)

**`07_protocols/` Protocols: MCP, A2A, REST (54-58):** 54 Notes MCP: Agno client, 55 Notes MCP: LangGraph client, 56 Research Agent as A2A Server, 57 Planner as A2A Client, 58 Research Agent REST API

## By industry

| Industry | Agents |
|----------|--------|
| Knowledge & RAG | 11, 13, 14, 17, 43, 48, 50, 51, 52 |
| Agent Patterns | 12, 16, 18, 19, 21, 23, 41, 44, 45 |
| Protocols | 54, 55, 56, 57, 58 |
| Software Dev | 09, 22, 37, 38 |
| Customer Service | 10, 20, 24, 31 |
| Finance | 04, 28, 39, 47 |
| Marketing | 29, 33, 34 |
| Data & Analytics | 15, 42, 49 |
| Entertainment & Gaming | 08, 36, 46 |
| Research | 01, 40, 53 |
| HR | 27, 30 |
| Banking | 25 |
| Education | 05 |
| Legal | 06 |
| Retail | 07 |
| Sales | 35 |
| Travel | 26 |
| Media | 02 |
| Lifestyle | 03 |
| Business Productivity | 32 |
