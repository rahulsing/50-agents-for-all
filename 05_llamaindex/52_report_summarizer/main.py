import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from llama_index.core import SimpleDirectoryReader, SummaryIndex
from llama_index.core.node_parser import SentenceSplitter

from common.llamaindex_setup import use_ollama

DEFAULT_REPORT = Path(__file__).parent / "sample_report.md"

QUESTIONS = {
    "Executive summary": "Write a 5-sentence executive summary of the whole report for a busy decision maker.",
    "Key numbers": "List the 6 most important numbers in the report, one bullet each with what they mean.",
    "Recommendations and deadlines": "List the recommendations and any deadlines or time-critical decisions.",
    "Risks and open problems": "List the main problems or risks the report identifies, one bullet each.",
}


def main() -> None:
    p = argparse.ArgumentParser(description="LlamaIndex long-report summarizer")
    p.add_argument("file", nargs="?", default=str(DEFAULT_REPORT), help="a .md, .txt or .pdf report")
    a = p.parse_args()
    path = Path(a.file)
    if not path.is_file():
        print(f"File not found: {path}")
        sys.exit(1)
    use_ollama()
    docs = SimpleDirectoryReader(input_files=[str(path)]).load_data()
    # Small chunks so the summary has to combine many pieces: tree_summarize summarises chunks in groups,
    # then summarises the summaries, so it works even when the report is longer than the model's context
    index = SummaryIndex.from_documents(docs, transformations=[SentenceSplitter(chunk_size=400, chunk_overlap=40)])
    engine = index.as_query_engine(response_mode="tree_summarize")
    print(f"Summarising {path.name} ({len(index.docstore.docs)} chunks)\n")
    for title, question in QUESTIONS.items():
        print(f"===== {title} =====\n{engine.query(question)}\n")


if __name__ == "__main__":
    main()
