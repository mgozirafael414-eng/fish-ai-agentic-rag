from app.rag.vector_store import search_chunks


# ============================================================
# RETRIEVE RELEVANT DOCUMENT CHUNKS
# ============================================================

def retrieve_relevant_chunks(
    query: str,
    n_results: int = 3,
) -> list[dict]:

    if not query or not query.strip():
        return []

    results = search_chunks(
        query=query,
        n_results=n_results,
    )

    documents = results.get(
        "documents",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]

    distances = results.get(
        "distances",
        [[]]
    )[0]

    retrieved_chunks = []

    for index, document in enumerate(
        documents
    ):

        metadata = {}

        if index < len(metadatas):
            metadata = metadatas[index]

        distance = None

        if index < len(distances):
            distance = distances[index]

        retrieved_chunks.append(
            {
                "content": document,
                "metadata": metadata,
                "distance": distance,
            }
        )

    return retrieved_chunks