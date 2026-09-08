from app.rag.document_loader import load_document
from app.rag.chunker import chunk_text
from app.rag.embeddings import generate_embeddings


# ============================================================
# LOAD DOCUMENT
# ============================================================

file_path = "data/documents/fish_notes.txt"

text = load_document(
    file_path
)


# ============================================================
# CREATE CHUNKS
# ============================================================

chunks = chunk_text(
    text,
    chunk_size=200,
    chunk_overlap=50,
)


print("=" * 60)
print("EMBEDDING TEST")
print("=" * 60)

print(
    "Total chunks:",
    len(chunks)
)


# ============================================================
# GENERATE EMBEDDINGS
# ============================================================

embeddings = generate_embeddings(
    chunks
)


print(
    "Total embeddings:",
    len(embeddings)
)


# ============================================================
# DISPLAY VECTOR INFORMATION
# ============================================================

if embeddings:

    print(
        "Vector dimension:",
        len(embeddings[0])
    )

    print()

    print(
        "First chunk:"
    )

    print(
        chunks[0]
    )

    print()

    print(
        "First embedding:"
    )

    print(
        embeddings[0]
    )
