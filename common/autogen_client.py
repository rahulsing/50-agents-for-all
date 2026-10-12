"""AutoGen model client for local Ollama models."""
from autogen_ext.models.ollama import OllamaChatCompletionClient

from common.llm import OLLAMA_URL


def ollama_client(model: str, tools: bool = True, temperature: float = 0.0) -> OllamaChatCompletionClient:
    # AutoGen only knows capabilities of models it recognises, so local models need an explicit model_info
    return OllamaChatCompletionClient(
        model=model,
        host=OLLAMA_URL,
        # No num_ctx here: every framework should use Ollama's default context for the same model, otherwise
        # concurrent requests with different sizes force Ollama to reload the model again and again
        options={"temperature": temperature},
        model_info={"vision": False, "function_calling": tools, "json_output": True,
                    "family": "unknown", "structured_output": True},
    )
