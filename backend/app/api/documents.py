from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.rag.document_loader import load_document
from app.rag.chunker import chunk_text
from app.rag.vector_store import (
    add_chunks,
    get_document_sources,
    delete_document,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"],
)


# ============================================================
# UPLOAD DIRECTORY
# ============================================================

UPLOAD_DIR = Path(
    "data/documents"
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# ALLOWED FILE TYPES
# ============================================================

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
}


# ============================================================
# UPLOAD DOCUMENT
# ============================================================

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    # ========================================================
    # CHECK FILE
    # ========================================================

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file selected."
        )


    # ========================================================
    # GET FILE EXTENSION
    # ========================================================

    extension = Path(
        file.filename
    ).suffix.lower()


    # ========================================================
    # CHECK FILE TYPE
    # ========================================================

    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Only PDF, DOCX, and TXT are allowed."
            )
        )


    # ========================================================
    # CREATE FILE PATH
    # ========================================================

    file_path = (
        UPLOAD_DIR /
        file.filename
    )


    # ========================================================
    # CHECK DUPLICATE DOCUMENT
    # ========================================================

    if file_path.exists():

        raise HTTPException(
            status_code=409,
            detail=(
                f"Document '{file.filename}' "
                "has already been uploaded."
            )
        )


    # ========================================================
    # SAVE FILE
    # ========================================================

    contents = await file.read()

    with open(
        file_path,
        "wb"
    ) as buffer:

        buffer.write(
            contents
        )


    # ========================================================
    # LOAD DOCUMENT
    # ========================================================

    try:

        text = load_document(
            str(file_path)
        )

    except Exception as error:

        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to load document: {error}"
            )
        )


    # ========================================================
    # CHECK DOCUMENT CONTENT
    # ========================================================

    if not text.strip():

        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=400,
            detail=(
                "The uploaded document contains "
                "no readable text."
            )
        )


    # ========================================================
    # CHUNK DOCUMENT
    # ========================================================

    chunks = chunk_text(
        text,
        chunk_size=500,
        chunk_overlap=100,
    )


    if not chunks:

        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=400,
            detail=(
                "No chunks could be created "
                "from the document."
            )
        )


    # ========================================================
    # STORE IN CHROMADB
    # ========================================================

    try:

        added_chunks = add_chunks(
            chunks=chunks,
            source=file.filename,
        )

    except Exception as error:

        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to store document: {error}"
            )
        )


    # ========================================================
    # SUCCESS RESPONSE
    # ========================================================

    return {
        "success": True,
        "message": "Document uploaded successfully.",
        "filename": file.filename,
        "chunks_created": len(chunks),
        "chunks_stored": added_chunks,
    }


# ============================================================
# LIST DOCUMENTS
# ============================================================

@router.get("/")
async def list_documents():

    documents = get_document_sources()

    return {
        "success": True,
        "documents": documents,
        "total_documents": len(documents),
    }


# ============================================================
# DELETE DOCUMENT
# ============================================================

@router.delete("/{filename}")
async def remove_document(
    filename: str
):

    file_path = (
        UPLOAD_DIR /
        filename
    )


    # ========================================================
    # CHECK FILE
    # ========================================================

    if not file_path.exists():

        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )


    # ========================================================
    # DELETE FROM CHROMADB
    # ========================================================

    try:

        deleted_chunks = delete_document(
            source=filename
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to delete document "
                f"from vector database: {error}"
            )
        )


    # ========================================================
    # DELETE PHYSICAL FILE
    # ========================================================

    try:

        file_path.unlink()

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to delete document file: "
                f"{error}"
            )
        )


    # ========================================================
    # SUCCESS RESPONSE
    # ========================================================

    return {
        "success": True,
        "message": "Document deleted successfully.",
        "filename": filename,
        "chunks_deleted": deleted_chunks,
    }