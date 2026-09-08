from app.rag.retriever import retrieve_relevant_chunks


# ============================================================
# TEST QUERY
# ============================================================

query = "What do tilapia eat?"


print("=" * 60)
print("RAG RETRIEVER TEST")
print("=" * 60)

print(
    "Query:",
    query
)


# ============================================================
# RETRIEVE CHUNKS
# ============================================================

results = retrieve_relevant_chunks(
    query=query,
    n_results=3,
)


print()
print(
    "Retrieved chunks:",
    len(results)
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

for index, result in enumerate(
    results,
    start=1
):

    print()
    print(
        f"--- RETRIEVED CHUNK {index} ---"
    )

    print(
        "Content:"
    )

    print(
        result["content"]
    )

    print()

    print(
        "Metadata:"
    )

    print(
        result["metadata"]
    )

    print()

    print(
        "Distance:"
    )

    print(
        result["distance"]
    )