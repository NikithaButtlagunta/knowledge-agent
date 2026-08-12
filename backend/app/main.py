from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel

from backend.app.agents.rag_agent import ask_knowledge_agent

from backend.app.ingestion.ingest import (
    ingest_pdf,
    list_documents,
    delete_document,
    get_document_info,
)


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="Knowledge Agent",
    description="A local RAG-based knowledge agent",
    version="0.1.0",
)


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

UPLOAD_DIR = (
    PROJECT_ROOT
    / "data"
    / "uploads"
)


# Create uploads directory
UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# REQUEST MODEL
# =========================================================

class ChatRequest(BaseModel):

    question: str

    history: list[dict] = []


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
async def health_check():

    return {
        "status": "healthy",
        "service": "knowledge-agent",
    }


# =========================================================
# UPLOAD PDF
# =========================================================

@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...)
):

    # -----------------------------------------------------
    # 1. Check file type
    # -----------------------------------------------------

    if not file.filename:

        return {
            "success": False,
            "message": "No filename provided.",
        }


    if not file.filename.lower().endswith(".pdf"):

        return {
            "success": False,
            "message": "Only PDF files are allowed.",
        }


    # -----------------------------------------------------
    # 2. Create file path
    # -----------------------------------------------------

    file_path = (
        UPLOAD_DIR
        / file.filename
    )


    # -----------------------------------------------------
    # 3. Save uploaded file
    # -----------------------------------------------------

    contents = await file.read()

    with open(
        file_path,
        "wb",
    ) as f:

        f.write(contents)


    # -----------------------------------------------------
    # 4. Create document ID
    # -----------------------------------------------------

    doc_id = Path(
        file.filename
    ).stem


    # -----------------------------------------------------
    # 5. Ingest document
    # -----------------------------------------------------

    ingestion_result = ingest_pdf(

        pdf_path=str(
            file_path
        ),

        doc_id=doc_id,

        source=file.filename,

        title=Path(
            file.filename
        ).stem,
    )


    # -----------------------------------------------------
    # 6. Handle duplicate
    # -----------------------------------------------------

    if ingestion_result.get(
        "duplicate"
    ):

        return {

            "success": False,

            "message": (
                "This PDF has already "
                "been uploaded and indexed."
            ),

            "document": ingestion_result,
        }


    # -----------------------------------------------------
    # 7. Return successful response
    # -----------------------------------------------------

    return {

        "success": True,

        "filename": file.filename,

        "message": (
            "PDF uploaded and "
            "indexed successfully."
        ),

        "ingestion": ingestion_result,
    }


# =========================================================
# LIST DOCUMENTS
# =========================================================

@app.get("/documents")
async def get_documents():

    documents = list_documents()

    return {

        "total_documents": len(
            documents
        ),

        "documents": documents,
    }

# =========================================================
# DELETE DOCUMENT
# =========================================================

@app.delete("/documents/{doc_id}")
async def remove_document(
    doc_id: str
):

    # Get document information
    document = get_document_info(
        doc_id
    )

    # Check if document exists
    if not document:

        return {
            "success": False,
            "message": "Document not found.",
            "doc_id": doc_id,
        }

    # Delete from ChromaDB and registry
    result = delete_document(
        doc_id
    )

    # Delete physical PDF file
    source = document.get(
        "source"
    )

    if source:

        file_path = (
            UPLOAD_DIR
            / source
        )

        if file_path.exists():

            file_path.unlink()

    return result


# =========================================================
# CHAT
# =========================================================

@app.post("/chat")
async def chat(
    request: ChatRequest
):

    result = await ask_knowledge_agent(
        request.question
    )

    return {

        "question": request.question,

        "answer": result[
            "answer"
        ],

        "sources": result[
            "sources"
        ],
    }