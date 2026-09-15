import json
import os

from langchain_core.documents import Document
from app.vector_store.chroma_store import seed_vector_store

PAPER_TITLES = {
    "1412_6980v9.pdf": "Adam: A Method for Stochastic Optimization",
    "buolamwini18a.pdf": "Gender Shades",
    "1607_06450v1.pdf": "Layer Normalization",
}

def get_paper_title(source_file):
    if source_file in PAPER_TITLES:
        return PAPER_TITLES[source_file]

    return os.path.splitext(source_file)[0].replace("_", " ").title()

def load_chunks(path):
    chunks = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                chunks.append(json.loads(line))

    return chunks

def chunks_to_documents(chunks):
    documents = []

    for chunk in chunks:
        metadata = {
            "chunk_id": chunk["chunk_id"],
            "source_file": chunk["source_file"],
            "paper_title": get_paper_title(chunk["source_file"]),
            "page_start": chunk["page_start"],
            "page_end": chunk["page_end"],
        }

        if chunk.get("section"):
            metadata["section"] = chunk["section"]

        documents.append(
            Document(
                page_content=chunk["text"],
                metadata=metadata,
            )
        )

    return documents

def load_documents(path):
    return chunks_to_documents(load_chunks(path))

def load_all_documents(directory):
    documents = []

    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".jsonl"):
            path = os.path.join(directory, filename)
            documents.extend(load_documents(path))

    return documents

if __name__ == "__main__":
    documents = load_all_documents("app/ingestion/output")

    seed_vector_store(
        documents,
        reset=True,
    )