import os

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("AGENT_MODEL", "qwen2.5:7b-instruct")
CODER_MODEL = os.getenv("CODER_MODEL", "qwen3-coder:30b")
EMBED_MODEL = os.getenv("EMBED_MODEL", "qwen3-embedding:latest")
# Larger model for agents where the 7B model is unreliable with several tools (e.g. agent 39)
STRONG_MODEL = os.getenv("STRONG_MODEL", "qwen2.5:14b-instruct")
