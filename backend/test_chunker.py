from app.rag.document_loader import load_document
from app.rag.chunker import chunk_text


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


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("=" * 60)
print("DOCUMENT CHUNKING TEST")
print("=" * 60)

print(
    "Total chunks:",
    len(chunks)
)

print()


for index, chunk in enumerate(
    chunks,
    start=1
):

    print(
        f"--- CHUNK {index} ---"
    )

    print(chunk)

    print()