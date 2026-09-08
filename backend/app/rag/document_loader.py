from pathlib import Path

from pypdf import PdfReader
from docx import Document


# ============================================================
# DOCUMENT LOADER
# ============================================================

def load_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    reader = PdfReader(file_path)

    pages = []

    for page in reader.pages:

        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n".join(pages)


# ============================================================
# DOCX LOADER
# ============================================================

def load_docx(file_path: str) -> str:
    """
    Extract text from a DOCX file.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:

        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    return "\n".join(paragraphs)


# ============================================================
# TEXT FILE LOADER
# ============================================================

def load_txt(file_path: str) -> str:
    """
    Load a normal text file.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


# ============================================================
# GENERIC DOCUMENT LOADER
# ============================================================

def load_document(file_path: str) -> str:
    """
    Automatically select the appropriate loader
    based on file extension.
    """

    extension = Path(
        file_path
    ).suffix.lower()


    if extension == ".pdf":

        return load_pdf(file_path)


    elif extension == ".docx":

        return load_docx(file_path)


    elif extension == ".txt":

        return load_txt(file_path)


    else:

        raise ValueError(
            f"Unsupported document type: {extension}"
        )