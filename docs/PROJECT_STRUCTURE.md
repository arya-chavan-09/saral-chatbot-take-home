# Project Structure

## app/chat

Responsible for the chatbot interface and user interaction flow.

### Key Responsibilities

* Command-line interaction
* User input handling
* Response display

---

## app/conversation

Maintains conversational state.

### Key Responsibilities

* Session management
* Chat history tracking
* Context preservation

---

## app/ingestion

Processes source PDFs into retrievable chunks.

### Key Responsibilities

* PDF parsing
* Section detection
* Chunk generation
* Metadata extraction

---

## app/retrieval

Finds relevant content from the vector database.

### Key Responsibilities

* Similarity search
* Ranking
* Context selection

---

## app/generation

Produces final answers using retrieved context.

### Key Responsibilities

* Prompt construction
* LLM interaction
* Response formatting

---

## app/evaluation

Measures chatbot quality.

### Key Responsibilities

* Retrieval evaluation
* Response evaluation
* Reporting

---

## app/db

Stores vector embeddings and retrieval indexes.

### Components

* ChromaDB collection
* Embedding metadata
* Vector index files
