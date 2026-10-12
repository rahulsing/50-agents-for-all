# Agent 39 - Currency Calculator (AutoGen)

## What it does
Ask currency questions in plain English ("How much is 250 USD in EUR and in INR?"). The agent calls a conversion tool once per currency pair, using live European Central Bank rates from the free Frankfurter API, and answers in a sentence.

## Concepts you learn
- **Function calling in AutoGen 0.7:** pass a plain Python function in `tools=[...]`. `Annotated[float, "..."]` type hints plus the docstring become the tool schema.
- **reflect_on_tool_use=True:** after the tool runs, the model gets a second turn to turn raw tool output into a natural answer. Without it, the agent's reply is just the tool result.
- **Parallel tool calls:** for two target currencies the model issues two calls in one step (visible in the `ToolCallRequestEvent`).
- **Graceful degradation:** if the rates API is unreachable, a fallback table is used and the answer says the rate is approximate.
- **`common/autogen_client.py`:** local models need an explicit `model_info` (function calling yes/no) because AutoGen does not know their capabilities.

## The flow
```
question -> model -> convert_currency(250, USD, EUR) + convert_currency(250, USD, INR) -> model -> answer
```

## Run
```
cd 50-agents-for-all
.venv-autogen\Scripts\python.exe 04_autogen\39_currency_calculator\main.py "How much is 250 USD in EUR and in INR?"
```
Empty question exits with code 1.

## Things to try
- Ask about an unknown currency code and see the error message reach the model.
- Set `reflect_on_tool_use=False` and compare the output.
- Add a second tool, `list_currencies()`.

## Known limits
- The first version pointed at an old API address and silently used the fallback rates; check the "(rate ..., source)" text in tool results.
- ECB rates are daily reference rates, not live trading rates.
