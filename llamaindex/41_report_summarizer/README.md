# Agent 41 - Report Summarizer (LlamaIndex)

## What it does
Summarises a long report (a fictional city mobility review is included) into four sections: an executive summary, the key numbers, recommendations and deadlines, and risks or open problems. Works with your own `.md`, `.txt` or `.pdf` file.

## Concepts you learn
- **SummaryIndex + tree_summarize:** unlike a vector index, a summary index uses *every* chunk. `tree_summarize` summarises groups of chunks, then summarises those summaries, so it works even when the report is longer than the model's context window.
- **Chunk size choice:** `SentenceSplitter(chunk_size=400)` splits even the short sample report into 3 chunks, so the tree has something to combine.
- **Several questions over one index:** the index is built once and queried four times with different instructions.

## The flow
```
report -> chunks (400 tokens) -> for each question: summarise chunk groups -> summarise the summaries -> section
```

## Run
```
cd 50-agents-for-all
.venv-llamaindex\Scripts\python.exe llamaindex\41_report_summarizer\main.py
.venv-llamaindex\Scripts\python.exe llamaindex\41_report_summarizer\main.py path\to\report.pdf
```
A missing file exits with code 1. PDFs need `pip install pypdf` in the LlamaIndex venv.

## Things to try
- Add a question to `QUESTIONS` (for example "Who is affected most?").
- Compare `response_mode="tree_summarize"` with `"compact"`.

## Known limits
- Every question reads every chunk, so long reports take a while.
- Check key numbers against the source: in a test it reported freight growth as "115%" when the report says 15%.
