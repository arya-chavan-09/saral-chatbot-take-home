from app.vector_store.chroma_store import similarity_search_with_scores

results = similarity_search_with_scores(
    "How does Adam perform bias correction?",
    k=5,
)

for doc, score in results:
    print("\nSCORE:", score)
    print("SOURCE:", doc.metadata["source_file"])
    print(
        "PAGES:",
        doc.metadata["page_start"],
        "-",
        doc.metadata["page_end"],
    )
    print("CHUNK:", doc.metadata["chunk_id"])
    print(doc.page_content[:300])