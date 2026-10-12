# Agent 43 - RAG Group Chat (AutoGen)

## What it does
Three agents answer questions from documents in `docs/` (a battery manual and cafe staff notes): a retriever searches, an answerer writes an answer citing file names, and a checker verifies every claim against the retrieved passages and replies "VERIFIED: ..." or lists unsupported claims.

## Concepts you learn
- **RAG from scratch:** `TinyVectorStore` is about 25 lines: split files into chunks, embed them with Ollama, normalise, and rank by cosine similarity with NumPy. No vector database needed for small data.
- **Chunking matters:** the first version split on blank lines, so a lone heading ("# SolarFlex 400 ...") became its own chunk and won a retrieval slot, while the warranty paragraph was missed. Headings are now glued to the paragraph that follows them.
- **Role separation:** retrieving, answering and checking are different agents with different prompts, in a `RoundRobinGroupChat`.
- **Honest failure:** when the passages don't contain the answer, the answerer says so and the checker confirms that.

## The chat
```
question -> retriever (search_docs, once per sub-question) -> answerer (cites files) -> checker -> VERIFIED
```

## Run
```
cd 50-agents-for-all
.venv-autogen\Scripts\python.exe 04_autogen\43_rag_group_chat\main.py "How long does a full solar charge of the SolarFlex take and what does the warranty exclude?"
```
Empty question exits with code 1. Add your own `.md`/`.txt` files to `docs/`.

## Things to try
- Change `k` in `search` and see how answers change.
- Compare with Agent 48 (LlamaIndex does the same pipeline for you).

## Known limits
- Embeddings are recomputed at every start (fine for small folders).
- Very short or very long paragraphs make poor chunks.
