import json
import hashlib
import time

from pathlib import Path

from langchain_core.documents import Document
from langchain_chroma import Chroma

from backend.app.config import (
    CHROMA_PATH,
    REGISTRY_PATH,
)

from backend.app.retrieval.embeddings import (
    get_embedding_model,
)

from backend.app.ingestion.pdf_loader import (
    extract_text_from_pdf,
)

from backend.app.ingestion.chunker import (
    chunk_pages,
)


# =========================================================
# VECTOR STORE
# =========================================================

def get_vector_store():
    """
    Return the existing ChromaDB vector store.
    """

    embedding_model = get_embedding_model()

    return Chroma(
        collection_name="knowledge_agent",
        persist_directory=str(CHROMA_PATH),
        embedding_function=embedding_model,
    )


# =========================================================
# DOCUMENT REGISTRY
# =========================================================

def load_registry():
    """
    Load the document registry.

    If the registry does not exist,
    return an empty list.
    """

    if not REGISTRY_PATH.exists():
        return []

    try:

        with open(
            REGISTRY_PATH,
            "r",
            encoding="utf-8",
        ) as f:

            return json.load(f)

    except (
        json.JSONDecodeError,
        OSError,
    ):

        return []


# =========================================================
# SAVE REGISTRY
# =========================================================

def save_registry(documents):
    """
    Save document information to the registry.
    """

    REGISTRY_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        REGISTRY_PATH,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            documents,
            f,
            indent=4,
        )


# =========================================================
# FILE HASH
# =========================================================

def calculate_file_hash(
    file_path: str
) -> str:
    """
    Calculate SHA-256 hash of a file.

    The same file will always produce
    the same hash.
    """

    sha256 = hashlib.sha256()

    with open(
        file_path,
        "rb",
    ) as f:

        while True:

            chunk = f.read(
                8192
            )

            if not chunk:
                break

            sha256.update(
                chunk
            )

    return sha256.hexdigest()


# =========================================================
# DUPLICATE CHECK
# =========================================================

def document_exists(
    file_hash: str
):
    """
    Check whether a document with the
    same file hash already exists.
    """

    registry = load_registry()

    for document in registry:

        if document.get(
            "file_hash"
        ) == file_hash:

            return document

    return None


# =========================================================
# INGEST PDF
# =========================================================

def ingest_pdf(
    pdf_path: str,
    doc_id: str,
    source: str,
    title: str,
):
    """
    Extract, chunk, embed, and store
    a PDF in ChromaDB.
    """

    start_time = time.time()

    print(
        "\n========================================"
    )

    print(
        "STARTING PDF INGESTION"
    )

    print(
        f"File: {source}"
    )

    print(
        "========================================"
    )


    # -----------------------------------------------------
    # 1. Calculate file hash
    # -----------------------------------------------------

    print(
        "1. Calculating file hash..."
    )

    file_hash = calculate_file_hash(
        pdf_path
    )

    print(
        "   ✓ File hash calculated"
    )


    # -----------------------------------------------------
    # 2. Check duplicate
    # -----------------------------------------------------

    print(
        "2. Checking for duplicate..."
    )

    existing_document = document_exists(
        file_hash
    )

    if existing_document:

        print(
            "   ✓ Duplicate document found"
        )

        return {
            "success": False,
            "duplicate": True,
            "message": (
                "This document has already "
                "been indexed."
            ),
            "doc_id": existing_document[
                "doc_id"
            ],
            "source": existing_document[
                "source"
            ],
            "chunks_created": 0,
        }


    print(
        "   ✓ Document is new"
    )


    # -----------------------------------------------------
    # 3. Extract PDF text
    # -----------------------------------------------------

    print(
        "3. Extracting PDF text..."
    )

    pages = extract_text_from_pdf(
        pdf_path
    )

    print(
        f"   ✓ Extracted {len(pages)} pages"
    )


    # -----------------------------------------------------
    # 4. Create chunks
    # -----------------------------------------------------

    print(
        "4. Creating chunks..."
    )

    chunks = chunk_pages(
        pages=pages,
        doc_id=doc_id,
        source=source,
        title=title,
    )

    print(
        f"   ✓ Created {len(chunks)} chunks"
    )


    # -----------------------------------------------------
    # 5. Convert chunks into Documents
    # -----------------------------------------------------

    print(
        "5. Creating document objects..."
    )

    documents = []

    ids = []

    for chunk in chunks:

        document = Document(
            page_content=chunk[
                "text"
            ],

            metadata={
                "doc_id": chunk[
                    "doc_id"
                ],

                "source": chunk[
                    "source"
                ],

                "title": chunk[
                    "title"
                ],

                "page": chunk[
                    "page"
                ],

                "chunk_id": chunk[
                    "chunk_id"
                ],

                "file_hash": file_hash,
            },
        )

        documents.append(
            document
        )

        ids.append(
            chunk[
                "chunk_id"
            ]
        )


    print(
        f"   ✓ Created "
        f"{len(documents)} Document objects"
    )


    # -----------------------------------------------------
    # 6. Load ChromaDB
    # -----------------------------------------------------

    print(
        "6. Loading ChromaDB..."
    )

    vector_store = get_vector_store()

    print(
        "   ✓ ChromaDB loaded"
    )


    # -----------------------------------------------------
    # 7. Add documents to ChromaDB
    # -----------------------------------------------------

    print(
        f"7. Adding "
        f"{len(documents)} documents to ChromaDB..."
    )

    print(
        "   Generating embeddings..."
    )

    embedding_start = time.time()

    vector_store.add_documents(
        documents=documents,
        ids=ids,
    )

    embedding_time = (
        time.time()
        - embedding_start
    )

    print(
        "   ✓ ChromaDB indexing "
        f"completed in "
        f"{embedding_time:.2f} seconds"
    )


    # -----------------------------------------------------
    # 8. Save document to registry
    # -----------------------------------------------------

    print(
        "8. Updating document registry..."
    )

    registry = load_registry()

    registry.append(
        {
            "doc_id": doc_id,
            "source": source,
            "title": title,
            "file_hash": file_hash,
            "chunks_created": len(
                documents
            ),
        }
    )

    save_registry(
        registry
    )

    print(
        "   ✓ Registry updated"
    )


    # -----------------------------------------------------
    # 9. Return result
    # -----------------------------------------------------

    total_time = (
        time.time()
        - start_time
    )

    print(
        "\n========================================"
    )

    print(
        "PDF INGESTION COMPLETE"
    )

    print(
        f"Total time: "
        f"{total_time:.2f} seconds"
    )

    print(
        "========================================\n"
    )


    return {
        "success": True,
        "duplicate": False,
        "message": (
            "Document indexed successfully."
        ),
        "doc_id": doc_id,
        "source": source,
        "chunks_created": len(
            documents
        ),
    }


# =========================================================
# LIST DOCUMENTS
# =========================================================

def list_documents():
    """
    Return all indexed documents.
    """

    registry = load_registry()

    return registry


# =========================================================
# DELETE DOCUMENT
# =========================================================

def delete_document(
    doc_id: str
):
    """
    Delete all chunks belonging to a document
    from ChromaDB and remove it from the registry.
    """

    # -----------------------------------------------------
    # 1. Load vector store
    # -----------------------------------------------------

    vector_store = get_vector_store()


    # -----------------------------------------------------
    # 2. Find chunks belonging to document
    # -----------------------------------------------------

    results = vector_store.get(
        where={
            "doc_id": doc_id
        }
    )

    document_ids = results.get(
        "ids",
        []
    )


    # -----------------------------------------------------
    # 3. Check document exists
    # -----------------------------------------------------

    if not document_ids:

        return {
            "success": False,
            "message": (
                "Document not found in ChromaDB."
            ),
            "doc_id": doc_id,
        }


    # -----------------------------------------------------
    # 4. Delete chunks
    # -----------------------------------------------------

    vector_store.delete(
        ids=document_ids
    )


    # -----------------------------------------------------
    # 5. Load registry
    # -----------------------------------------------------

    registry = load_registry()


    # -----------------------------------------------------
    # 6. Find deleted document
    # -----------------------------------------------------

    deleted_document = None

    for document in registry:

        if document.get(
            "doc_id"
        ) == doc_id:

            deleted_document = document

            break


    # -----------------------------------------------------
    # 7. Update registry
    # -----------------------------------------------------

    updated_registry = [

        document

        for document in registry

        if document.get(
            "doc_id"
        ) != doc_id

    ]

    save_registry(
        updated_registry
    )


    # -----------------------------------------------------
    # 8. Return result
    # -----------------------------------------------------

    return {
        "success": True,

        "message": (
            "Document deleted successfully."
        ),

        "doc_id": doc_id,

        "chunks_deleted": len(
            document_ids
        ),

        "document": deleted_document,
    }


# =========================================================
# GET DOCUMENT INFO
# =========================================================

def get_document_info(
    doc_id: str
):
    """
    Find document information in the registry.
    """

    registry = load_registry()

    for document in registry:

        if document.get(
            "doc_id"
        ) == doc_id:

            return document

    return None