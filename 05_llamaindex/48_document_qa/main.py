import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from llama_index.core import PromptTemplate, Settings, SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama

from common.llm import DEFAULT_MODEL, EMBED_MODEL, OLLAMA_URL

DEFAULT_DOCS = Path(__file__).parent / "docs"
MIN_SCORE = 0.3  # chunks less similar than this are dropped before answering

QA_PROMPT = PromptTemplate(
    "Context from the user's documents:\n{context_str}\n\n"
    "Answer the question using ONLY the context above. "
    "If the context does not contain the answer, reply exactly: "
    "I could not find this in the documents.\n"
    "Question: {query_str}\nAnswer:"
)


def build_query_engine(docs_dir: Path):
    Settings.llm = Ollama(model=DEFAULT_MODEL, base_url=OLLAMA_URL, request_timeout=180, temperature=0)
    Settings.embed_model = OllamaEmbedding(model_name=EMBED_MODEL, base_url=OLLAMA_URL)
    documents = SimpleDirectoryReader(str(docs_dir)).load_data()
    index = VectorStoreIndex.from_documents(documents)
    return index.as_query_engine(
        similarity_top_k=3,
        node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=MIN_SCORE)],
        text_qa_template=QA_PROMPT,
    )


def main() -> None:
    p = argparse.ArgumentParser(description="LlamaIndex document Q&A")
    p.add_argument("question", nargs="?", default="")
    p.add_argument("--docs", type=Path, default=DEFAULT_DOCS, help="folder with .txt/.md/.pdf files")
    a = p.parse_args()
    if not a.question.strip():
        print("Please provide a question.")
        sys.exit(1)
    if not a.docs.is_dir() or not any(a.docs.iterdir()):
        print(f"No documents found in {a.docs}")
        sys.exit(1)

    response = build_query_engine(a.docs).query(a.question.strip())
    if not response.source_nodes:  # nothing passed the similarity cutoff
        print("\nI could not find this in the documents.")
        return
    print("\n" + str(response))
    print("\nSources:")
    for n in response.source_nodes:
        print(f"- {n.node.metadata.get('file_name', '?')} (score {n.score:.2f})")


if __name__ == "__main__":
    main()
