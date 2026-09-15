# Assumptions

## Document Scope

The chatbot answers questions only from documents that have been ingested into the vector store.

## Retrieval Strategy

Top matching chunks are assumed to provide sufficient context for answer generation.

## Embeddings

Embedding quality directly influences retrieval accuracy.

## Session Context

Recent conversation history is assumed to improve answer continuity.

# Limitations

## Retrieval Errors

Relevant passages may be missed when wording differs significantly from source content.

## Context Window Constraints

Large documents may contain information that cannot fit into a single prompt.

## Hallucination Risk

The language model may occasionally generate unsupported details.

## Citation Support

Responses depend on retrieved chunks and may not provide complete source attribution.

## Small Corpus Bias

Performance measurements are influenced by the size and diversity of the ingested document set.

# Evaluation Methodology

## Retrieval Quality

Metrics:

* Recall@K
* Precision@K
* Relevance inspection

## Response Quality

Criteria:

* Correctness
* Grounding
* Completeness
* Clarity

## Human Evaluation

Evaluators review:

* Factual accuracy
* Source consistency
* Helpfulness
* Conversational quality

# Future Improvements

* Hybrid keyword + vector retrieval
* Reranking models
* Citation generation
* Multi-document reasoning
* Streaming responses
* Web interface
* Automated benchmark suite
* Response confidence scoring
