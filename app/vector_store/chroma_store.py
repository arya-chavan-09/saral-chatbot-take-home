import os

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_ollama import OllamaEmbeddings

EMBEDDING_MODEL = "nomic-embed-text"
COLLECTION_NAME = "research_papers"

APP_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DB_PATH = os.path.join(
    APP_DIR,
    "db",
    "research_papers",
)

def get_embeddings() -> Embeddings: 
    return OllamaEmbeddings(model=EMBEDDING_MODEL)

def get_vector_store(embeddings: Embeddings | None = None,) -> Chroma:
    os.makedirs(DB_PATH, exist_ok=True)

    return Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=DB_PATH,
        embedding_function=embeddings or get_embeddings(),
    )

def seed_vector_store(documents: list[Document], batch_size: int = 100, reset: bool = False,) -> Chroma:
    store = get_vector_store()

    if reset:
        store.delete_collection()
        store = get_vector_store()

    if not documents:
        return store

    for start in range(0, len(documents), batch_size):
        batch = documents[start:start + batch_size]

        ids = [
            doc.metadata["chunk_id"]
            for doc in batch
        ]

        store.add_documents(
            documents=batch,
            ids=ids,
        )

    return store

def get_retriever(search_kwargs: dict | None = None, search_type: str = "similarity", source_file: str | None = None,):
    store = get_vector_store()
    kwargs = search_kwargs or {"k": 5}

    if source_file:
        kwargs = {
            **kwargs,
            "filter": {"source_file": source_file},
        }

    return store.as_retriever(
        search_type=search_type,
        search_kwargs=kwargs,
    )

def similarity_search_with_scores(query: str, k: int = 5, source_file: str | None = None,) -> list[tuple[Document, float]]:
    store = get_vector_store()
    filter_ = (
        {"source_file": source_file}
        if source_file
        else None
    )

    return store.similarity_search_with_relevance_scores(
        query,
        k=k,
        filter=filter_,
    )