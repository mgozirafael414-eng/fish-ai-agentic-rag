
# ============================================================
# EMBEDDING SERVICE
# ============================================================

from functools import lru_cache

from sentence_transformers import SentenceTransformer


# ============================================================
# EMBEDDING MODEL
# ============================================================

MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _get_embedding_model() -> SentenceTransformer:
    print(
        f"[EMBEDDINGS] Loading model: {MODEL_NAME}"
    )

    model = SentenceTransformer(
        MODEL_NAME
    )

    print(
        "[EMBEDDINGS] Model loaded successfully."
    )

    return model


# ============================================================
# EMBED SINGLE TEXT
# ============================================================

def generate_embedding(
    text: str
) -> list[float]:
    """
    Convert one text into an embedding vector.
    """

    if not text or not text.strip():
        raise ValueError(
            "Text cannot be empty."
        )

    embedding = _get_embedding_model().encode(
        text,
        convert_to_numpy=True,
    )

    return embedding.tolist()


# ============================================================
# EMBED MULTIPLE TEXTS
# ============================================================

def generate_embeddings(
    texts: list[str]
) -> list[list[float]]:
    """
    Convert multiple texts into embedding vectors.
    """

    if not texts:
        return []

    embeddings = _get_embedding_model().encode(
        texts,
        convert_to_numpy=True,
    )

    return embeddings.tolist()

