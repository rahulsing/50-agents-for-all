"""Example client for the REST API: calls /health, then /ask/stream and prints tokens as they arrive."""
import json
import sys

import httpx

BASE = "http://localhost:8000"


def main() -> None:
    question = " ".join(sys.argv[1:]).strip() or "What is retrieval augmented generation?"
    try:
        print("health:", httpx.get(f"{BASE}/health", timeout=5).json())
    except httpx.ConnectError:
        print(f"API not running at {BASE}. Start it with: .venv-agno\\Scripts\\python.exe "
              "07_protocols\\58_research_rest_api\\api.py")
        sys.exit(1)
    with httpx.stream("POST", f"{BASE}/ask/stream", json={"question": question}, timeout=300) as r:
        for line in r.iter_lines():
            if line.startswith("data: "):
                token = json.loads(line[6:])
                if token != "[DONE]":
                    print(token, end="", flush=True)
    print()


if __name__ == "__main__":
    main()
