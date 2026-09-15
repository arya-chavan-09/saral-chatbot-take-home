# Saral Research Chatbot

## Overview

This project is a Retrieval Augmented Generation (RAG) chatbot that answers questions from a collection of research papers. The system ingests PDF documents, extracts and chunks content, generates embeddings, stores them in ChromaDB, retrieves relevant passages, and uses an LLM to generate grounded responses.

## Features

* PDF document ingestion
* Intelligent text chunking
* Vector search using ChromaDB
* Conversational question answering
* Session-based chat history
* Automated evaluation pipeline
* Human evaluation template
* Modular architecture

## Architecture

```text
PDF Documents
      ↓
 PDF Parser
      ↓
 Section Detection
      ↓
 Text Chunking
      ↓
 Embedding Generation
      ↓
 ChromaDB Vector Store
      ↓
 Retriever
      ↓
 Prompt Builder
      ↓
 LLM Generator
      ↓
 Final Response
```

## Installation

```bash
git clone <repository-url>
cd saral-chatbot

python -m venv .venv

source .venv/bin/activate
# Windows
# .venv\Scripts\activate

pip install -r requirements.txt
```

## Run PDF Ingestion

```bash
python main.py ingest
```

## Run Chatbot

```bash
python main.py chat
```

## Run Evaluation

```bash
python main.py evaluate
```

## Repository Structure

```text
app/
├── chat/
├── conversation/
├── db/
├── evaluation/
├── generation/
├── ingestion/
└── retrieval/

docs/
example_runs/
raw_pdfs/
```

## Sample Question
User:
What are the main findings of the Gender Shades paper?

Assistant:
The paper demonstrates significant disparities in commercial gender classification systems across demographic groups...
Design Goals
Accurate retrieval
Grounded responses
Maintainable architecture
Reproducible evaluation
Clear separation of concerns
