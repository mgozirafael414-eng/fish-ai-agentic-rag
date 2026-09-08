import os
import uuid
import chromadb

from app.rag.embeddings import generate_embedding


# ============================================================
# CHROMADB CONFIGURATION
# ============================================================

CHROMA_PATH = "data/chroma_db"

COLLECTION_NAME = "fish_knowledge"


# ============================================================
# GET COLLECTION
# ============================================================

def get_collection():

    os.makedirs(
        CHROMA_PATH,
        exist_ok=True
    )

    client = chromadb.PersistentClient(
        path=CHROMA_PATH
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    return collection


# ============================================================
# ADD CHUNKS
# ============================================================

def add_chunks(
    chunks: list[str],
    source: str,
):

    if not chunks:
        return 0

    collection = get_collection()

    embeddings = []

    for chunk in chunks:

        embedding = generate_embedding(
            chunk
        )

        embeddings.append(
            embedding
        )

    ids = [
        str(uuid.uuid4())
        for _ in chunks
    ]

    metadatas = [
        {
            "source": source,
            "chunk_index": index,
        }
        for index in range(
            len(chunks)
        )
    ]

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print(
        f"[VECTOR STORE] Added "
        f"{len(chunks)} chunks from {source}"
    )

    return len(chunks)


# ============================================================
# SEARCH CHUNKS
# ============================================================

def search_chunks(
    query: str,
    n_results: int = 3,
):

    if not query or not query.strip():
        return []

    collection = get_collection()

    total_documents = collection.count()

    if total_documents == 0:
        return []

    n_results = min(
        n_results,
        total_documents
    )

    query_embedding = generate_embedding(
        query
    )

    results = collection.query(
        query_embeddings=[
            query_embedding
        ],
        n_results=n_results,
    )

    return results


# ============================================================
# GET COLLECTION COUNT
# ============================================================

def get_collection_count():

    collection = get_collection()

    return collection.count()


# ============================================================
# GET ALL DOCUMENT SOURCES
# ============================================================

def get_document_sources():

    collection = get_collection()

    total_documents = collection.count()

    if total_documents == 0:
        return []

    results = collection.get(
        include=[
            "metadatas"
        ]
    )

    metadatas = results.get(
        "metadatas",
        []
    )

    sources = {}

    for metadata in metadatas:

        if not metadata:
            continue

        source = metadata.get(
            "source"
        )

        if not source:
            continue

        if source not in sources:

            sources[source] = 0

        sources[source] += 1

    documents = []

    for source, chunks in sources.items():

        documents.append(
            {
                "filename": source,
                "chunks": chunks,
            }
        )

    return documents


# ============================================================
# DELETE DOCUMENT FROM VECTOR STORE
# ============================================================

def delete_document(
    source: str
):

    collection = get_collection()

    results = collection.get(
        where={
            "source": source
        }
    )

    ids = results.get(
        "ids",
        []
    )

    if not ids:
        return 0

    collection.delete(
        ids=ids
    )

    print(
        f"[VECTOR STORE] Deleted "
        f"{len(ids)} chunks from {source}"
    )

    return len(ids)