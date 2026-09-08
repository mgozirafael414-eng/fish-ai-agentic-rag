from app.rag.document_loader import load_document


file_path = "data/documents/fish_notes.txt"


text = load_document(file_path)


print("=" * 60)
print("DOCUMENT LOADED SUCCESSFULLY")
print("=" * 60)

print(text)

print("=" * 60)

print(
    "Number of characters:",
    len(text)
)