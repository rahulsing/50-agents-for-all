"""Point LlamaIndex at local Ollama instead of its OpenAI default."""
from llama_index.core import Settings
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama

from common.llm import DEFAULT_MODEL, EMBED_MODEL, OLLAMA_URL


def use_ollama(model: str = DEFAULT_MODEL, context_window: int = 32768) -> None:
    # LlamaIndex sends context_window to Ollama as num_ctx; 32768 matches Ollama's default for qwen2.5,
    # so all frameworks share one loaded copy of the model instead of forcing reloads
    Settings.llm = Ollama(model=model, base_url=OLLAMA_URL, request_timeout=300, temperature=0,
                          context_window=context_window)
    Settings.embed_model = OllamaEmbedding(model_name=EMBED_MODEL, base_url=OLLAMA_URL)
