from app.rag.document_loader import load_document
from app.rag.chunker import chunk_text

from app.rag.vector_store import (
    add_chunks,
    search_chunks,
    get_collection_count,
)


# ============================================================
# LOAD DOCUMENT
# ============================================================

file_path = "data/documents/fish_notes.txt"

text = load_document(
    file_path
)


# ============================================================
# CHUNK DOCUMENT
# ============================================================

chunks = chunk_text(
    text,
    chunk_size=200,
    chunk_overlap=50,
)


print("=" * 60)
print("CHROMADB VECTOR STORE TEST")
print("=" * 60)

print(
    "Total chunks:",
    len(chunks)
)


# ============================================================
# STORE CHUNKS
# ============================================================

added = add_chunks(
    chunks=chunks,
    source="fish_notes.txt",
)

print(
    "Chunks added:",
    added
)


# ============================================================
# DATABASE COUNT
# ============================================================

count = get_collection_count()

print(
    "Total vectors in database:",
    count
)


# ============================================================
# SEARCH
# ============================================================

query = "What do tilapia eat?"

print()
print(
    "Search query:",
    query
)

results = search_chunks(
    query=query,
    n_results=3,
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print()
print("=" * 60)
print("SEARCH RESULTS")
print("=" * 60)

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


for index, document in enumerate(
    documents,
    start=1
):

    print()
    print(
        f"--- RESULT {index} ---"
    )

    print(
        "Document:"
    )

    print(
        document
    )

    print(
        "Metadata:"
    )

    print(
        metadatas[index - 1]
    )

    print(
        "Distance:"
    )

    print(
        distances[index - 1]
    )