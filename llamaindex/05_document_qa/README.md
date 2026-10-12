# Agent 05 - Document Q&A (LlamaIndex)

## What it does
Ask a question about the files in a folder. It finds the most relevant passages, answers from them only, and lists which files and how strongly each matched. Two sample documents are included (a battery manual and cafe staff notes); point `--docs` at your own folder to use real files.

## Concepts you learn
- **LlamaIndex model:** it is a *data framework* for RAG. You load documents, build an index, then ask the index questions. No agent loop is needed.
- **Pipeline:** load, split into chunks, embed, store in a vector index, retrieve top matches, send them with the question to the LLM.
- **Query engine:** `index.as_query_engine()` bundles retrieval and answering in one object.
- **Postprocessors:** the `SimilarityPostprocessor` drops weak matches before they reach the LLM.
- **Prompt control:** a custom QA prompt forces "answer only from the context".
- **Compare with Agent 02:** there retrieval was a tool the LLM chose to call (agentic). Here retrieval always runs first (classic RAG), which is simpler and more predictable.

## The flow
```
documents -> chunks -> embeddings -> VectorStoreIndex (in memory)
question -> embed -> top 3 chunks -> drop score < 0.3 -> LLM answers from them -> answer + sources
                                            \--> nothing left? "I could not find this in the documents."
```

## How the code works (`main.py`)
1. `Settings.llm` / `Settings.embed_model` set LlamaIndex to use local Ollama (`common/llm.py`) instead of its OpenAI default.
2. `SimpleDirectoryReader` loads every file in the folder (txt, md, pdf and more).
3. `VectorStoreIndex.from_documents` chunks, embeds and indexes them. Rebuilt each run.
4. `as_query_engine(similarity_top_k=3, node_postprocessors=[...], text_qa_template=QA_PROMPT)` retrieves, filters, and answers.
5. Sources come from `response.source_nodes` with their file names and scores.

## Run
```
cd 50-agents-for-all
.venv-llamaindex\Scripts\python.exe llamaindex\05_document_qa\main.py "How long does the SolarFlex take to charge from solar?"
.venv-llamaindex\Scripts\python.exe llamaindex\05_document_qa\main.py "Your question" --docs C:\path\to\your\folder
```
Empty question prints a message and exits with code 1; so does an empty or missing docs folder.

## Things to try
- Ask about the cafe, then about the battery, and check the Sources lines.
- Ask something not in the files ("capital of France") and confirm it declines.
- Change `MIN_SCORE` to 0.0 and ask the same off-topic question: without the cutoff the model starts answering from its own knowledge or noise.
- Raise `similarity_top_k` to 5 and see whether answers change.
- Drop a PDF into `docs/` (you may need `pip install pypdf`).

## Known limits
- The cutoff of 0.3 is tuned for `qwen3-embedding` on these sample files; a different embedding model or document type may need a different value.
- Index is rebuilt every run and kept in memory only (slow for big folders).
- Sources list can include a weakly related file that still passed the cutoff.
