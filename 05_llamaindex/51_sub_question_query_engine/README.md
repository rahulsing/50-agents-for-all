# Agent 51 - Sub-Question Query Engine (LlamaIndex)

## What it does
Answers comparison questions across two company reports (Northwind and Fresco; fictional 2025 summaries). It breaks your question into one sub-question per company and topic, answers each from the right document, then combines them.

## Concepts you learn
- **Query decomposition:** `SubQuestionQueryEngine` asks the LLM to produce sub-questions, each tagged with the tool (document) that should answer it. With `verbose=True` you see every sub-question and its answer.
- **Why it helps:** a plain RAG search for "compare revenue growth of A and B" often retrieves only one company's text; splitting guarantees both are looked up.
- **Same tools, different engine:** the per-document `QueryEngineTool`s look like Agent 50's, but here a fixed decompose-then-merge pipeline replaces the agent's free choice.
- **Works with any LLM:** `SubQuestionQueryEngine.from_defaults` tries to load an OpenAI-specific question generator by default and fails without that package. Passing `question_gen=LLMQuestionGenerator.from_defaults()` uses a plain prompt instead, which works with Ollama.

## The flow
```
question -> LLM writes sub-questions -> [northwind tool, fresco tool, ...] -> sub-answers -> combined answer
```

## Run
```
cd 50-agents-for-all
.venv-llamaindex\Scripts\python.exe 05_llamaindex\51_sub_question_query_engine\main.py "Compare the revenue growth, operating margin and online sales share of Northwind and Fresco"
```
Empty question exits with code 1.

## Things to try
- Ask a question about only one company and see it create fewer sub-questions.
- Add a third company report to `docs/`.

## Known limits
- A sub-question can come back empty (in a test, Fresco's operating margin), and the final answer then says "not provided".
- The final merge is done by the 7B model and can draw the wrong conclusion from correct sub-answers (in a test it said Fresco grew faster, although the sub-answers said 4% vs 12%). Read the sub-answers, not just the summary.
