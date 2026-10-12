# Lessons learned: making small local models reliable

Every agent here was run against a 7B model, and many failed the first time in instructive ways. These are the patterns that fixed them. Each links to the agent where it happened.

## 1. Let the model decide; let code act and calculate

Small models are good at judgement and language, bad at arithmetic and at following procedures exactly.

- **Scores:** asked for a 0-100 score, a model gave a candidate missing half the requirements 85/100, and another answered on a 0-10 scale so no lead ever passed the threshold. Fix: the model judges each criterion (yes/no + evidence); code computes the score. ([30](agents/03_crewai/30_recruitment_workflow.md), [35](agents/03_crewai/35_lead_score_flow.md))
- **Maths:** totals, rankings and "best/worst month" are computed in Python; the model only explains them. ([25](agents/02_langgraph/25_bank_statement_analyst.md), [47](agents/04_autogen/47_stock_portfolio_watcher.md))
- **Side effects:** a support agent with a `create_ticket` tool invented email addresses and even ticket numbers. Fix: the model returns `escalate: true`, and code opens the ticket only with a real email from the message. ([10](agents/01_agno/10_support_agent.md))

## 2. Verify claims against real tool output

- A reviewer agent wrote correct SQL, then **typed an imaginary result table instead of running it** and approved its own invented numbers. Fix: a termination condition that accepts an approval only if its numbers appear in a real query result. ([42](agents/04_autogen/42_nl_to_sql.md))
- A planner returned an empty list of questions and silently answered from memory instead of calling the remote agent. Fix: fall back to sending the whole goal. ([57](agents/07_protocols/57_planner_a2a_client.md))

## 3. Enforce the workflow in code when prompts are ignored

- A researcher kept doing the maths itself and finishing early, so the analyst with the calculator never ran, even when told not to. Fix: a rule in the router: only the analyst may finish. ([18](agents/02_langgraph/18_supervisor_multi_agent.md), [23](agents/02_langgraph/23_multi_agent_collaboration.md))
- Chess players skipped their move tools and just typed moves as chat. Fix: code runs the game loop, shows the legal moves, and validates every move. ([46](agents/04_autogen/46_conversational_chess.md))

## 4. Give the model the context; don't make it explore

- A README generator listed the wrong folder, got nothing, and invented a whole project. Fix: code lists the files and puts them in the prompt. ([09](agents/01_agno/09_readme_generator.md))
- An SQL agent guessed column names before reading the schema. Fix: put the schema in the system prompt. ([42](agents/04_autogen/42_nl_to_sql.md))

## 5. One document (or clause) per call

- Asked to review a whole contract in one structured reply, the model returned an empty clause list. Split by clause, it reviewed every one. ([06](agents/01_agno/06_legal_document_analysis.md))
- CVs are screened one per task. ([30](agents/03_crewai/30_recruitment_workflow.md))

## 6. Keep structured outputs small

- Asking for a long answer plus a critique in one JSON object made the model emit whitespace for 20+ minutes, blocking Ollama for every other program. With a length cap, the JSON was cut off instead. Fix: write the answer as plain text; only the short critique is structured. ([19](agents/02_langgraph/19_reflexion_agent.md))

## 7. Guardrails need care too

- A salary rule that matched any currency amount rejected "customer deposits of £25 billion" on every retry. ([27](agents/03_crewai/27_job_posting_generator.md))
- "Cut it to under 450 words" produced the same text each retry: small models can't count. Feedback must say *what* to change.
- LangChain's PII middleware only cleans the *last* user message; in a multi-agent graph the original message still reached other agents. Fix: clean the input once at the graph's entry. ([18](agents/02_langgraph/18_supervisor_multi_agent.md))

See all of them on the [Guardrails](guardrails.md) page.

## 8. Running models locally

- **Context size:** `qwen3-coder:30b` defaults to a 262k-token context; loaded that way it spilled onto the CPU and blocked Ollama. Set `num_ctx` (e.g. 16384) for such models. CrewAI talks to Ollama through the OpenAI-compatible endpoint, which can't set it, so CrewAI agents use the 7B model.
- **Mixed context sizes:** different programs requesting the same model with different `num_ctx` force constant reloads; under load Ollama stalled. Use the same size everywhere and run tests one at a time.
- **Tool calling varies by model:** `llama3.1:8b` printed tool calls as text; `qwen2.5:7b-instruct` executed them.
- **Free web search is flaky:** the shared `web_search` retries several backends.

## 9. Library details that cost time

| Library | Gotcha |
|---------|--------|
| Agno 3.x | The Ollama model needs the `openai` package; `SqliteDb` needs `greenlet`; `MCPTools` needs `fastmcp`; a guardrail stop returns `status == error` instead of raising |
| LangGraph / LangChain 1.x | `create_agent` lives in `langchain.agents`; the in-memory vector store needs `numpy` |
| CrewAI 1.x | `result.raw` is only the last task (use `tasks_output`); the console needs UTF-8 on Windows |
| AutoGen 0.7 | Local models need an explicit `model_info`; small models write TERMINATE in the same message as code |
| LlamaIndex | `SubQuestionQueryEngine` needs `LLMQuestionGenerator` without the OpenAI package; `context_window` is sent to Ollama as `num_ctx` |
| MCP | SDK 2.x renamed `FastMCP` to `MCPServer` |
| A2A | `a2a-sdk` 1.x uses protobuf types and route helpers; older tutorials' `A2AStarletteApplication` is gone; raise the client timeout |
