from pathlib import Path

from langchain_chroma import Chroma

from backend.app.retrieval.embeddings import get_embedding_model


# =========================================================
# PROJECT PATH
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

CHROMA_PATH = PROJECT_ROOT / "data" / "chroma_db"


# =========================================================
# GET VECTOR STORE
# =========================================================

def get_vector_store():
    """
    Return the existing ChromaDB vector store.
    """

    embedding_model = get_embedding_model()

    vector_store = Chroma(
        collection_name="knowledge_agent",
        persist_directory=str(CHROMA_PATH),
        embedding_function=embedding_model,
    )

    return vector_store


# =========================================================
# SEMANTIC SEARCH
# =========================================================

def search_documents(
    question: str,
    k: int = 8
):
    """
    Search ChromaDB using semantic similarity.

    Returns documents together with their similarity scores.
    """

    vector_store = get_vector_store()

    results = vector_store.similarity_search_with_score(
        question,
        k=k
    )

    return results


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    question = input(
        "Enter your question: "
    )

    results = search_documents(
        question
    )

    print(
        "\nSearch Results:\n"
    )

    for index, (document, score) in enumerate(
        results,
        start=1
    ):

        print(
            f"Result {index}"
        )

        print(
            f"Score: {score}"
        )

        print(
            f"Source: {document.metadata.get('source')}"
        )

        print(
            f"Page: {document.metadata.get('page')}"
        )

        print(
            f"Chunk ID: {document.metadata.get('chunk_id')}"
        )

        print(
            f"Text: {document.page_content[:300]}"
        )

        print(
            "-" * 60
        )