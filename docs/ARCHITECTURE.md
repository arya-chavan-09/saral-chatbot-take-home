# SARAL Chatbot — Architecture

## System Overview

The application is a Retrieval-Augmented Generation (RAG) chatbot built around a collection of research papers. Documents are parsed, chunked, embedded, stored in ChromaDB, retrieved at query time, and used to generate grounded responses with source provenance.

## Pipeline Diagram

```mermaid
flowchart TD

    subgraph Ingestion["1. Document Ingestion"]
        PDF[PDF Research Papers] --> Parser["pdf_parser.py"]
        Parser --> Chunker["chunker.py"]
        Chunker --> Section["section_detector.py"]
        Section --> Pipeline["pdf_pipeline.py"]
        Pipeline --> JSONL["Chunked JSONL Output"]
    end

    subgraph Indexing["2. Vector Indexing"]
        JSONL --> Seeder["seed_documents.py"]
        Seeder --> Embed["Embedding Model"]
        Embed --> Chroma[(ChromaDB)]
    end

    subgraph Retrieval["3. Retrieval"]
        User["User Query"] --> Retriever["chroma_store.py"]
        Chroma --> Retriever
        Retriever --> Context["Relevant Chunks"]
    end

    subgraph Generation["4. Response Generation"]
        Context --> Prompt["prompts.py"]
        Prompt --> Provider["llm_provider.py"]
        Provider --> Generator["generator.py"]
        Generator --> Answer["Generated Response"]
    end

    subgraph Provenance["5. Provenance"]
        Answer --> Citation["citation.py"]
        Citation --> Sources["Chunk References"]
    end

    subgraph Conversation["6. Session Management"]
        User --> Session["session.py"]
        Session --> Generator
        Generator --> Session
    end

    subgraph Evaluation["7. Evaluation"]
        Answer --> Metrics["metrics.py"]
        Metrics --> Eval["run_eval.py"]
        Eval --> Report["Evaluation Report"]
    end
```

---

# Module Map

| Layer        | Module                              | Responsibility                                  |
| ------------ | ----------------------------------- | ----------------------------------------------- |
| Chat         | `app/chat/cli.py`                   | Command-line chatbot interface                  |
| Conversation | `app/conversation/session.py`       | Maintains conversation state and history        |
| Ingestion    | `app/ingestion/pdf_parser.py`       | Extracts text from PDF documents                |
| Ingestion    | `app/ingestion/chunker.py`          | Splits documents into retrieval-friendly chunks |
| Ingestion    | `app/ingestion/section_detector.py` | Identifies document sections and metadata       |
| Ingestion    | `app/ingestion/pdf_pipeline.py`     | End-to-end ingestion workflow                   |
| Ingestion    | `app/ingestion/seed_documents.py`   | Loads processed chunks into the vector store    |
| Vector Store | `app/vector_store/chroma_store.py`  | ChromaDB integration and retrieval logic        |
| Generation   | `app/generation/prompts.py`         | Prompt construction templates                   |
| Generation   | `app/generation/llm_provider.py`    | LLM abstraction layer                           |
| Generation   | `app/generation/generator.py`       | Retrieval and generation orchestration          |
| Provenance   | `app/provenance/citation.py`        | Citation extraction and source mapping          |
| Evaluation   | `app/evaluation/metrics.py`         | Evaluation metrics implementation               |
| Evaluation   | `app/evaluation/run_eval.py`        | Automated evaluation pipeline                   |

---

# Retrieval Flow

1. User submits a question through the CLI.
2. The query is sent to the Chroma retriever.
3. Relevant chunks are fetched from the vector store.
4. Retrieved context is injected into a prompt template.
5. The selected LLM generates a response.
6. Citation information is attached to the output.
7. Conversation history is stored for subsequent turns.

---

# Design Decisions

## ChromaDB for Retrieval

ChromaDB provides lightweight local vector storage with efficient similarity search. This keeps the system easy to run and suitable for a take-home assignment without requiring external infrastructure.

## Modular LLM Layer

`llm_provider.py` separates model access from business logic. New providers can be added without modifying retrieval or conversation code.

## Persistent Conversation State

Session management is isolated in `session.py`, allowing follow-up questions to retain context across turns.

## Source-Aware Responses

The provenance layer links generated answers back to retrieved document chunks, improving transparency and supporting evaluation.

## Offline Evaluation

The evaluation package allows retrieval and answer quality to be measured independently of the interactive chat workflow.

---

# Data Storage

```text
raw_pdfs/
├── research papers

app/ingestion/output/
├── processed JSONL chunks

app/db/research_papers/
├── chroma.sqlite3
└── vector index files
```