"""Import this BEFORE crewai: disables telemetry and makes the Windows console print CrewAI's emoji safely."""
import os
import sys

os.environ.setdefault("CREWAI_DISABLE_TELEMETRY", "true")
os.environ.setdefault("OTEL_SDK_DISABLED", "true")
for _stream in (sys.stdout, sys.stderr):
    _stream.reconfigure(encoding="utf-8", errors="replace")


def ollama_llm(model: str, temperature: float = 0.3):
    """CrewAI talks to Ollama using the 'ollama/<model>' name.

    CrewAI uses Ollama's OpenAI-compatible endpoint, which cannot set the context size (num_ctx) per request,
    so Ollama uses the model's default. Avoid models whose default is huge (qwen3-coder: 262k tokens) here."""
    from crewai import LLM

    from common.llm import OLLAMA_URL
    return LLM(model=f"ollama/{model}", base_url=OLLAMA_URL, temperature=temperature)
