# =========================================================
# RETRIEVER
# =========================================================

from backend.app.retrieval.vector_store import get_vector_store


# =========================================================
# SEARCH DOCUMENTS
# =========================================================

def search_documents(
    query: str,
    k: int = 8
):
    """
    Search ChromaDB for documents relevant to the query.

    Returns:
        List of tuples:
        (Document, score)

    Chroma similarity scores are distance scores,
    where LOWER is generally better.
    """

    if not query or not query.strip():
        return []

    try:

        vector_store = get_vector_store()

        results = vector_store.similarity_search_with_score(
            query,
            k=k
        )

        if not results:
            return []

        cleaned_results = []

        for document, score in results:

            if document is None:
                continue

            if not document.page_content:
                continue

            cleaned_results.append(
                (
                    document,
                    float(score)
                )
            )

        return cleaned_results

    except Exception as e:

        print(
            f"[Retriever Error] {e}"
        )

        return []