# ============================================================
# DOCUMENT CHUNKER
# ============================================================


def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100,
) -> list[str]:
    """
    Split a document into overlapping text chunks.

    Parameters:
        text: Full document text
        chunk_size: Maximum number of characters per chunk
        chunk_overlap: Number of overlapping characters

    Returns:
        List of text chunks
    """

    if not text:
        return []

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than 0."
        )

    if chunk_overlap < 0:
        raise ValueError(
            "chunk_overlap cannot be negative."
        )

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size."
        )


    # --------------------------------------------------------
    # Clean text
    # --------------------------------------------------------

    text = " ".join(
        text.split()
    )


    chunks = []

    start = 0
    text_length = len(text)


    # --------------------------------------------------------
    # Create chunks
    # --------------------------------------------------------

    while start < text_length:

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)


        # Move forward while keeping overlap

        start = end - chunk_overlap


    return chunks

