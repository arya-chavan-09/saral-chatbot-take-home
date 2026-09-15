# Saral Research Chatbot

## Overview

This project is a Retrieval Augmented Generation (RAG) chatbot that answers questions from a collection of research papers. The system ingests PDF documents, extracts and chunks content, generates embeddings, stores them in ChromaDB, retrieves relevant passages, and uses an LLM to generate grounded responses.

## Features

* PDF document ingestion
* Intelligent section-aware text chunking
* Dense semantic retrieval using MXBAI-Embed-Large embeddings
* ChromaDB vector database
* Audience-adaptive script generation
* Slide bullet generation
* Speaker notes and presentation scripts
* Provenance and citation tracking
* Conversational refinement and iterative editing
* Session-based chat history
* Automated evaluation pipeline
* Human evaluation template
* Modular RAG architecture
* Gemini 3.6 Flash generation support

---

## Architecture

```text
PDF Documents
      ↓
PDF Parser
      ↓
Section Detection
      ↓
Math-Aware Text Chunking
      ↓
MXBAI Embeddings
      ↓
ChromaDB Vector Store
      ↓
Retriever
      ↓
Prompt Builder
      ↓
Gemini 3.6 Flash
      ↓
Scripts / Bullets / Speaker Notes
      ↓
Provenance & Citations
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

---

## Gemini Setup (Optional)

### Create API Key

Generate an API key from Google AI Studio:

https://aistudio.google.com/app/apikey

### Configure Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_api_key_here
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
