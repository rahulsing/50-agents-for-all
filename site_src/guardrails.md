# Guardrails

A **guardrail** checks what goes into or comes out of a model, and blocks, cleans or retries when a rule is broken. Three agents show each framework's **built-in** guardrail feature; several others use **hand-written** guardrails, plain code that stops a small model's typical mistakes.

In every agent's code, search for `GUARDRAIL` to jump to the relevant lines.

## Framework built-in guardrails

| Agent | Framework feature | What it guards |
|-------|-------------------|----------------|
| [10 Support Agent](agents/01_agno/10_support_agent.md) | **Agno** `pre_hooks` with `PromptInjectionGuardrail` and `PIIDetectionGuardrail`, plus a custom `post_hooks` check | Blocks prompt-injection messages and card/IBAN/SSN numbers *before* the model is called; blocks replies that contain card-like numbers or leak instructions |
| [27 Job Posting Generator](agents/03_crewai/27_job_posting_generator.md) | **CrewAI** `Task(guardrails=[function, "plain-English rule"], guardrail_max_retries=3)` | Length, biased wording, required sections and invented salaries (code); discriminatory requirements (checked by an LLM). Failures go back to the agent for a rewrite |
| [18 Supervisor Multi-Agent](agents/02_langgraph/18_supervisor_multi_agent.md) | **LangChain middleware** `PIIMiddleware`, `ModelCallLimitMiddleware`, `ToolCallLimitMiddleware`, plus a PII node at the graph's entry | Redacts emails and masks card numbers for the whole team; caps model and tool calls per worker |

### What each looks like in code

=== "Agno (agent 10)"

    ```python
    agent = Agent(
        model=...,
        pre_hooks=[PromptInjectionGuardrail(), PIIDetectionGuardrail(enable_email_check=False)],
        post_hooks=[output_guardrail],   # your own function; raise OutputCheckError to block
    )
    run = agent.run(message)
    if run.status == RunStatus.error:    # a guardrail stopped the run (it returns, it doesn't raise)
        print("Blocked:", run.content)
    ```

=== "CrewAI (agent 27)"

    ```python
    def posting_rules(result: TaskOutput) -> tuple[bool, Any]:
        if len(result.raw.split()) > 450:
            return False, "Too long: shorten About us to 2 sentences ..."   # feedback for the retry
        return True, result

    review = Task(..., guardrails=[posting_rules,
                                   "The posting must not contain requirements based on age or gender ..."],
                  guardrail_max_retries=3)
    ```

=== "LangChain / LangGraph (agent 18)"

    ```python
    researcher = create_agent(llm, [web_search], middleware=[
        PIIMiddleware("email", strategy="redact"),
        PIIMiddleware("credit_card", strategy="mask"),
        ModelCallLimitMiddleware(run_limit=5, exit_behavior="end"),
        ToolCallLimitMiddleware(tool_name="web_search", run_limit=2),
    ])
    ```

## Hand-written guardrails

| Agent | Guardrail |
|-------|-----------|
| [15 SQL Agent](agents/02_langgraph/15_sql_agent.md), [42 NL to SQL](agents/04_autogen/42_nl_to_sql.md) | The database is opened read-only and only SELECT queries are accepted |
| [42 NL to SQL](agents/04_autogen/42_nl_to_sql.md) | `VerifiedApproval`: an approval only counts if its numbers appear together in a real query result row |
| [18 Supervisor](agents/02_langgraph/18_supervisor_multi_agent.md), [23 Collaboration](agents/02_langgraph/23_multi_agent_collaboration.md) | Workflow order enforced in the router: the analyst must check the numbers before the run can finish |
| [10 Support Agent](agents/01_agno/10_support_agent.md) | The model only decides to escalate; code opens the ticket, and only with a real email from the message |
| [30 Recruitment](agents/03_crewai/30_recruitment_workflow.md), [35 Lead Score](agents/03_crewai/35_lead_score_flow.md) | Scores are computed in code from the model's yes/no judgements |
| [46 Chess](agents/04_autogen/46_conversational_chess.md) | A referee in code validates every proposed move |
| [38 Code Loop](agents/04_autogen/38_code_feedback_loop.md), [22 Code Assistant](agents/02_langgraph/22_code_assistant.md) | Model-written code runs in a separate process with a timeout |

## What testing taught about guardrails

- **Too broad means blocked forever.** A "no salary" rule matching any currency amount rejected "customer deposits of £25 billion" on every retry.
- **Feedback must be actionable.** "Under 450 words" got the same 473-word text back each time; "shorten About us to 2 sentences, at most 4 bullets per section" worked.
- **LLM guardrails are not deterministic.** The fairness rule caught "under 30, male preferred", but once also rejected a clean posting. Put hard rules in code; use LLM guardrails for judgement.
- **Protect the whole system, not just one agent.** LangChain's PII middleware cleans only the *last* user message; in a multi-agent graph other agents still saw the raw email and card number until the input was cleaned at the graph's entry.
- **Blocked inputs are cheap.** A blocked message never reaches the model, so the answer comes back in about 3 seconds instead of 20.
