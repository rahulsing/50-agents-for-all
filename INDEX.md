# Agent Index

58 local agents on Ollama: the main 50 across five frameworks, plus 8 extras (Anthropic SDK, MCP, A2A, REST API, banking and a stock portfolio). Every folder has a `main.py` (or a server file), a learning-oriented `README.md` and a `requirements.txt`. The order is the build order, from simple to advanced.

Setup, run commands and shared code (`common/`) are described in [CLAUDE.md](CLAUDE.md); each README has the exact command for that agent.

## Guardrails: where to look

Agents marked **[Guardrail]** in the tables below demonstrate guardrails. In each file, search for `GUARDRAIL` to jump to the code; each README has a "Guardrails" section explaining it.

**Framework built-in guardrails**

| # | Agent | Framework feature | What it guards | Code |
|---|-------|-------------------|----------------|------|
| 39 | Support Agent | Agno `pre_hooks` / `post_hooks` with `PromptInjectionGuardrail`, `PIIDetectionGuardrail` + a custom output check | Blocks prompt injection and card/IBAN/SSN numbers before the model runs; blocks replies that leak numbers or instructions | [main.py#L27](agno/39_support_agent/main.py#L27), [hooks](agno/39_support_agent/main.py#L89) |
| 09 | Job Posting Generator | CrewAI `Task(guardrails=[...], guardrail_max_retries=3)`: a function guardrail + a plain-English LLM guardrail | Length, biased wording, required sections, invented salary, discriminatory requirements; failures are sent back for a rewrite | [main.py#L19](crewai/09_job_posting_generator/main.py#L19), [task](crewai/09_job_posting_generator/main.py#L90) |
| 31 | Supervisor Multi-Agent | LangChain middleware: `PIIMiddleware`, `ModelCallLimitMiddleware`, `ToolCallLimitMiddleware` + a graph-entry PII node | Redacts emails and masks cards for the whole team; caps model and tool calls per worker | [main.py#L34](langgraph/31_supervisor_multi_agent/main.py#L34), [entry node](langgraph/31_supervisor_multi_agent/main.py#L137) |

**Hand-written guardrails** (plain code that stops a small model's mistakes)

| # | Agent | Guardrail | Code |
|---|-------|-----------|------|
| 21, 25 | SQL agents | Database opened read-only; only SELECT queries accepted | [21](langgraph/21_sql_agent/main.py#L23), [25](autogen/25_nl_to_sql/main.py#L25) |
| 25 | Natural Language to SQL | `VerifiedApproval`: an approval counts only if its numbers appear in a real query result | [main.py#L50](autogen/25_nl_to_sql/main.py#L50) |
| 31, 47 | Supervisor / Collaboration | Workflow order enforced in code (the analyst must check numbers before finishing) | [31](langgraph/31_supervisor_multi_agent/main.py#L106), [47](langgraph/47_multi_agent_collaboration/main.py#L52) |
| 39 | Support Agent | The model only decides to escalate; code opens the ticket, and only with a real email | [main.py#L122](agno/39_support_agent/main.py#L122) |
| 23, 43 | Recruitment / Lead Score | Scores computed in code from the model's yes/no judgements | [23](crewai/23_recruitment_workflow/main.py#L28), [43](crewai/43_lead_score_flow/main.py#L28) |
| 48 | Conversational Chess | A referee in code validates every move | [main.py#L41](autogen/48_conversational_chess/main.py#L41) |
| 04, 45 | Code agents | Model-written code runs in a separate process with a timeout | [04](autogen/04_code_feedback_loop/), [45](langgraph/45_code_assistant/) |

## All agents, in build order

| # | Agent | Framework | Industry | What it does |
|---|-------|-----------|----------|--------------|
| 01 | [Research Agent](agno/01_research_agent/) | Agno | Research | Web search, then a 5-bullet answer with sources |
| 02 | [Agentic RAG](langgraph/02_agentic_rag/) | LangGraph | Knowledge & RAG | Decides when to search a handbook, answers with the section cited |
| 03 | [Trip Planner](crewai/03_trip_planner/) | CrewAI | Travel | Researcher, planner and budgeter crew for a city trip |
| 04 | [Code Exec Feedback Loop](autogen/04_code_feedback_loop/) | AutoGen | Software Dev | Coder writes Python, executor runs it, errors feed back |
| 05 | [Document Q&A](llamaindex/05_document_qa/) | LlamaIndex | Knowledge & RAG | Questions over a folder of your own documents, with sources |
| 06 | [YouTube Agent](agno/06_youtube_agent/) | Agno | Media | Summarises a YouTube video or answers questions from its transcript |
| 07 | [Recipe Creator](agno/07_recipe_creator/) | Agno | Lifestyle | One recipe from your ingredients, as structured output |
| 08 | [Reflection Agent](langgraph/08_reflection_agent/) | LangGraph | Agent Patterns | Writes, critiques and rewrites its own draft |
| 09 | [Job Posting Generator](crewai/09_job_posting_generator/) | CrewAI | HR | **[Guardrail]** Researches a company, drafts and reviews a job posting |
| 10 | [Currency Calculator](autogen/10_currency_calculator/) | AutoGen | Finance | Function calling with live ECB exchange rates |
| 11 | [CSV / SQL Query](llamaindex/11_csv_sql_query/) | LlamaIndex | Data & Analytics | Natural-language questions over a CSV via text-to-SQL |
| 12 | [Finance Agent](agno/12_finance_agent/) | Agno | Finance | Live stock data (price, ratios, analysts) explained in a table |
| 13 | [Corrective RAG](langgraph/13_corrective_rag/) | LangGraph | Knowledge & RAG | Grades retrieved text; falls back to web search when it is irrelevant |
| 14 | [Stock Analysis](crewai/14_stock_analysis/) | CrewAI | Finance | Data analyst, news researcher and writer produce a stock report |
| 15 | [Web Search Agent](autogen/15_web_search_agent/) | AutoGen | Research | Searches, reads pages, answers with sources |
| 16 | [Study Partner](agno/16_study_partner/) | Agno | Education | Interactive tutor and quiz with saved sessions |
| 17 | [Self-RAG](langgraph/17_self_rag/) | LangGraph | Knowledge & RAG | Checks its own answer for grounding and usefulness, retries |
| 18 | [Marketing Strategy Generator](crewai/18_marketing_strategy/) | CrewAI | Marketing | Market research turned into a structured marketing plan |
| 19 | [Group Chat](autogen/19_group_chat/) | AutoGen | Agent Patterns | An LLM manager picks who speaks next among planner, researcher, writer |
| 20 | [Multi-Document Agent](llamaindex/20_multi_document_agent/) | LlamaIndex | Knowledge & RAG | An agent with facts and summary tools per document (city guides) |
| 21 | [SQL Agent](langgraph/21_sql_agent/) | LangGraph | Data & Analytics | Explores a read-only database, writes and fixes SQL |
| 22 | [Legal Document Analysis](agno/22_legal_document_analysis/) | Agno | Legal | Clause-by-clause contract risk review from your side |
| 23 | [Recruitment Workflow](crewai/23_recruitment_workflow/) | CrewAI | HR | Evidence-based CV screening, interview questions, shortlist |
| 24 | [Plan-and-Execute](langgraph/24_plan_and_execute/) | LangGraph | Agent Patterns | Plans steps, executes them with a sub-agent, re-plans |
| 25 | [Natural Language to SQL](autogen/25_nl_to_sql/) | AutoGen | Data & Analytics | **[Guardrail]** SQL writer plus a reviewer agent that approves the query |
| 26 | [Shopping Partner](agno/26_shopping_partner/) | Agno | Retail | Searches a store catalog with plain-function tools |
| 27 | [Email Auto Responder](crewai/27_email_auto_responder/) | CrewAI | Customer Service | A Flow that triages an inbox, alerts on urgent mail, drafts replies |
| 28 | [Adaptive RAG](langgraph/28_adaptive_rag/) | LangGraph | Knowledge & RAG | Routes each question to handbook, web or a direct answer |
| 29 | [Movie Recommendation](agno/29_movie_recommendation/) | Agno | Entertainment | Recommends from a movie list and remembers you between runs |
| 30 | [Sub-Question Query Engine](llamaindex/30_sub_question_query_engine/) | LlamaIndex | Knowledge & RAG | Splits a comparison into per-document sub-questions |
| 31 | [Supervisor Multi-Agent](langgraph/31_supervisor_multi_agent/) | LangGraph | Agent Patterns | **[Guardrail]** A supervisor routes work to researcher, analyst and writer |
| 32 | [Meeting Prep](crewai/32_meeting_prep/) | CrewAI | Business Productivity | Company and industry research into a one-page briefing |
| 33 | [RAG Group Chat](autogen/33_rag_group_chat/) | AutoGen | Knowledge & RAG | Retriever, answerer and checker agents with a tiny vector store |
| 34 | [README Generator](agno/34_readme_generator/) | Agno | Software Dev | Reads a project folder (read-only) and writes its README |
| 35 | [Reflexion Agent](langgraph/35_reflexion_agent/) | LangGraph | Agent Patterns | Self-critique that triggers web searches, then a revised answer |
| 36 | [Instagram Post Generator](crewai/36_instagram_post_generator/) | CrewAI | Marketing | Hierarchical crew with an auto-created manager |
| 37 | [Nested Chats](autogen/37_nested_chats/) | AutoGen | Agent Patterns | A whole review team used as one tool of a writer agent |
| 38 | [Customer Support](langgraph/38_customer_support/) | LangGraph | Customer Service | Intent routing, order tools, human approval for refunds |
| 39 | [Support Agent](agno/39_support_agent/) | Agno | Customer Service | **[Guardrail]** Knowledge-base answers; code opens tickets when the model escalates |
| 40 | [Landing Page Generator](crewai/40_landing_page_generator/) | CrewAI | Marketing | Analyst, copywriter and coder build a single-file HTML page |
| 41 | [Report Summarizer](llamaindex/41_report_summarizer/) | LlamaIndex | Knowledge & RAG | Tree-summarises a long report into summary, numbers, risks |
| 42 | [Hierarchical Agent Teams](langgraph/42_hierarchical_agent_teams/) | LangGraph | Agent Patterns | A top supervisor over a research team and a writing team |
| 43 | [Lead Score Flow](crewai/43_lead_score_flow/) | CrewAI | Sales | A Flow that BANT-scores leads and emails the hot ones |
| 44 | [Society of Mind](autogen/44_society_of_mind/) | AutoGen | Agent Patterns | An inner writer/editor team acting as one agent |
| 45 | [Code Assistant](langgraph/45_code_assistant/) | LangGraph | Software Dev | Structured code generation, executed and fixed until it runs |
| 46 | [Screenplay Writer](crewai/46_screenplay_writer/) | CrewAI | Entertainment | Turns a forum thread into a screenplay scene |
| 47 | [Multi-Agent Collaboration](langgraph/47_multi_agent_collaboration/) | LangGraph | Agent Patterns | Researcher and analyst pass the baton until the analyst signs off |
| 48 | [Conversational Chess](autogen/48_conversational_chess/) | AutoGen | Gaming | Two LLM players; tools enforce legal moves |
| 49 | [Information Gathering](langgraph/49_information_gathering/) | LangGraph | Customer Service | Asks questions until it can write a prompt template |
| 50 | [Markdown Validator](crewai/50_markdown_validator/) | CrewAI | Software Dev | Code lints Markdown; the agent explains and fixes it |

## Extras

| # | Agent | Framework | Industry | What it does |
|---|-------|-----------|----------|--------------|
| 51 | [Research Agent (plain SDK)](anthropic_sdk/51_research_agent/) | Anthropic SDK | Research | Agent 01 rebuilt with the Anthropic SDK pointed at Ollama, hand-written tool loop |
| 52 | [Notes MCP: Agno client](protocols/52_notes_mcp_agno/) | Agno + MCP | Protocols | Agent uses tools from a local MCP server ([notes_mcp_server.py](protocols/notes_mcp_server.py)) |
| 53 | [Notes MCP: LangGraph client](protocols/53_notes_mcp_langgraph/) | LangGraph + MCP | Protocols | The same MCP server used from a second framework |
| 54 | [Research Agent as A2A Server](protocols/54_research_a2a_server/) | Agno + A2A | Protocols | Publishes an agent card and answers A2A requests |
| 55 | [Planner as A2A Client](protocols/55_planner_a2a_client/) | LangGraph + A2A | Protocols | Discovers agent 54 and delegates research to it |
| 56 | [Research Agent REST API](protocols/56_research_rest_api/) | Agno + FastAPI | Protocols | `/ask` (JSON) and `/ask/stream` (SSE) endpoints |
| 57 | [Bank Statement Analyst](langgraph/57_bank_statement_analyst/) | LangGraph | Banking | Categorises spending, flags unusual transactions, suggests a budget (synthetic data) |
| 58 | [Stock Portfolio Watcher](autogen/58_stock_portfolio_watcher/) | AutoGen | Finance | Portfolio value, P/L and indicators, then a risk review (not financial advice) |

## By framework

**Agno (10 + extras 52, 54, 56):** 01 Research, 06 YouTube, 07 Recipe, 12 Finance, 16 Study Partner, 22 Legal, 26 Shopping, 29 Movie Recommendation, 34 README Generator, 39 Support Agent

**LangGraph (14 + extras 53, 55, 57):** 02 Agentic RAG, 08 Reflection, 13 Corrective RAG, 17 Self-RAG, 21 SQL Agent, 24 Plan-and-Execute, 28 Adaptive RAG, 31 Supervisor, 35 Reflexion, 38 Customer Support, 42 Hierarchical Teams, 45 Code Assistant, 47 Multi-Agent Collaboration, 49 Information Gathering

**CrewAI (12):** 03 Trip Planner, 09 Job Posting, 14 Stock Analysis, 18 Marketing Strategy, 23 Recruitment, 27 Email Auto Responder, 32 Meeting Prep, 36 Instagram Post, 40 Landing Page, 43 Lead Score, 46 Screenplay Writer, 50 Markdown Validator

**AutoGen (9 + extra 58):** 04 Code Feedback Loop, 10 Currency Calculator, 15 Web Search, 19 Group Chat, 25 Natural Language to SQL, 33 RAG Group Chat, 37 Nested Chats, 44 Society of Mind, 48 Conversational Chess

**LlamaIndex (5):** 05 Document Q&A, 11 CSV / SQL Query, 20 Multi-Document Agent, 30 Sub-Question Query Engine, 41 Report Summarizer

**Anthropic SDK (extra):** 51 Research Agent (plain SDK)

## By industry

| Industry | Agents |
|----------|--------|
| Knowledge & RAG | 02, 05, 13, 17, 20, 28, 30, 33, 41 |
| Agent Patterns | 08, 19, 24, 31, 35, 37, 42, 44, 47 |
| Protocols | 52, 53, 54, 55, 56 |
| Software Dev | 04, 34, 45, 50 |
| Customer Service | 27, 38, 39, 49 |
| Finance | 10, 12, 14, 58 |
| Marketing | 18, 36, 40 |
| Data & Analytics | 11, 21, 25 |
| Entertainment & Gaming | 29, 46, 48 |
| Research | 01, 15, 51 |
| HR | 09, 23 |
| Banking | 57 |
| Education | 16 |
| Legal | 22 |
| Retail | 26 |
| Sales | 43 |
| Travel | 03 |
| Media | 06 |
| Lifestyle | 07 |
| Business Productivity | 32 |
