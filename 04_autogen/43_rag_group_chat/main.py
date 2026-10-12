import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np
import ollama
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console

from common.autogen_client import ollama_client
from common.llm import DEFAULT_MODEL, EMBED_MODEL, OLLAMA_URL

DOCS = Path(__file__).parent / "docs"


class TinyVectorStore:
    """A minimal vector store: split files into paragraphs, embed them, and search by cosine similarity."""

    def __init__(self, folder: Path):
        self.client = ollama.Client(host=OLLAMA_URL)
        self.chunks = [(p.name, chunk) for p in sorted(folder.glob("*.*"))
                       for chunk in self._split(p.read_text(encoding="utf-8"))]
        self.vectors = self._embed([c[1] for c in self.chunks])

    @staticmethod
    def _split(text: str) -> list[str]:
        """Split on blank lines, but glue a heading-only paragraph onto the paragraph after it."""
        chunks, pending = [], ""
        for para in (p.strip() for p in text.split("\n\n")):
            if not para:
                continue
            if para.startswith("#") and "\n" not in para:  # a lone heading: keep it with the next paragraph
                pending = f"{pending}\n{para}".strip()
                continue
            chunks.append(f"{pending}\n{para}".strip())
            pending = ""
        return chunks

    def _embed(self, texts: list[str]) -> np.ndarray:
        v = np.array(self.client.embed(model=EMBED_MODEL, input=texts)["embeddings"])
        return v / np.linalg.norm(v, axis=1, keepdims=True)

    def search(self, query: str, k: int = 3) -> list[tuple[str, str, float]]:
        scores = self.vectors @ self._embed([query])[0]
        return [(*self.chunks[i], float(scores[i])) for i in np.argsort(-scores)[:k]]


STORE = TinyVectorStore(DOCS)


def search_docs(query: str) -> str:
    """Search the company documents. Returns the 3 best matching passages with their file names."""
    return "\n\n".join(f"[{name}, score {s:.2f}] {text}" for name, text, s in STORE.search(query))


async def run(question: str) -> None:
    client = ollama_client(DEFAULT_MODEL)
    retriever = AssistantAgent("retriever", model_client=client, tools=[search_docs],
                               system_message="Call search_docs to find passages for the user's question. If the "
                                              "question has several parts, call search_docs once per part. Do not "
                                              "answer the question.")
    answerer = AssistantAgent("answerer", model_client=client,
                              system_message="Answer the question using ONLY the retrieved passages. Cite file "
                                             "names. If the passages do not contain the answer, say so.")
    checker = AssistantAgent("checker", model_client=client,
                             system_message="Verify every claim in the answer against the passages. If all are "
                                            "supported, reply 'VERIFIED: <the answer>'. Otherwise list the "
                                            "unsupported claims.")
    team = RoundRobinGroupChat([retriever, answerer, checker], termination_condition=(
        TextMentionTermination("VERIFIED", sources=["checker"]) | MaxMessageTermination(7)))
    await Console(team.run_stream(task=question))
    await client.close()


def main() -> None:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        print("Please provide a question about the documents.")
        sys.exit(1)
    asyncio.run(run(question))


if __name__ == "__main__":
    main()
