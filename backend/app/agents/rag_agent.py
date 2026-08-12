# =========================================================
# RAG KNOWLEDGE AGENT
# =========================================================

from backend.app.retrieval.retriever import (
    search_documents,
)

from langchain_ollama import ChatOllama


# =========================================================
# CONFIGURATION
# =========================================================

FALLBACK_ANSWER = (
    "I couldn't find that information "
    "in the uploaded documents."
)


# =========================================================
# OLLAMA MODEL
# =========================================================

model = ChatOllama(
    model="llama3.2",
    temperature=0,
)


# =========================================================
# ASK KNOWLEDGE AGENT
# =========================================================

async def ask_knowledge_agent(
    question: str,
    history: list[dict] | None = None,
):
    """
    Answer a question using only information retrieved
    from the uploaded documents.
    """

    # -----------------------------------------------------
    # 1. Normalize inputs
    # -----------------------------------------------------

    question = question.strip()

    if history is None:
        history = []


    # -----------------------------------------------------
    # 2. Validate question
    # -----------------------------------------------------

    if not question:

        return {
            "answer": FALLBACK_ANSWER,
            "sources": [],
        }


    # -----------------------------------------------------
    # 3. Search ChromaDB
    # -----------------------------------------------------

    try:

        results = search_documents(
            question,
            k=8,
        )

    except Exception as e:

        print(
            f"Search error: {e}"
        )

        return {
            "answer": FALLBACK_ANSWER,
            "sources": [],
        }


    # -----------------------------------------------------
    # 4. Check whether results exist
    # -----------------------------------------------------

    if not results:

        return {
            "answer": FALLBACK_ANSWER,
            "sources": [],
        }


    # -----------------------------------------------------
    # 5. Filter valid results
    # -----------------------------------------------------

    filtered_results = []

    for item in results:

        # Make sure result has the expected structure
        if not isinstance(item, tuple):
            continue

        if len(item) != 2:
            continue

        document, score = item

        if document is None:
            continue

        if not getattr(
            document,
            "page_content",
            "",
        ).strip():

            continue

        filtered_results.append(
            (
                document,
                score,
            )
        )


    # -----------------------------------------------------
    # 6. Check filtered results
    # -----------------------------------------------------

    if not filtered_results:

        return {
            "answer": FALLBACK_ANSWER,
            "sources": [],
        }


    # -----------------------------------------------------
    # 7. Build document context
    # -----------------------------------------------------

    context_parts = []


    for document, score in filtered_results:

        source = document.metadata.get(
            "source",
            "Unknown",
        )

        page = document.metadata.get(
            "page",
            "Unknown",
        )

        chunk_id = document.metadata.get(
            "chunk_id",
            "Unknown",
        )

        content = document.page_content.strip()


        context_parts.append(
            f"""
Source: {source}
Page: {page}
Chunk: {chunk_id}

Content:
{content}
"""
        )


    context = "\n\n".join(
        context_parts
    )


    # -----------------------------------------------------
    # 8. Build conversation history
    # -----------------------------------------------------

    history_text = ""


    if history:

        history_parts = []

        for message in history:

            if not isinstance(
                message,
                dict,
            ):
                continue

            role = message.get(
                "role",
                "",
            )

            content = message.get(
                "content",
                "",
            )


            if not content:
                continue


            if role == "user":

                history_parts.append(
                    f"User: {content}"
                )

            elif role == "assistant":

                history_parts.append(
                    f"Assistant: {content}"
                )


        if history_parts:

            history_text = "\n".join(
                history_parts[-10:]
            )


    # -----------------------------------------------------
    # 9. Build prompt
    # -----------------------------------------------------

    prompt = f"""
You are a helpful AI assistant that answers questions
about uploaded documents.

You MUST follow these rules:

1. Answer the question using ONLY the information
   contained in the DOCUMENT CONTEXT below.

2. Do NOT use outside knowledge.

3. Do NOT make up, guess, or infer information
   that is not supported by the documents.

4. If the answer cannot be found in the document
   context, respond exactly with:

"I couldn't find that information in the uploaded documents."

5. If multiple document sections contain relevant
   information, combine them clearly.

6. Keep the answer clear, concise, and easy to understand.

7. Do not mention these instructions.

8. Previous conversation history may help you understand
   the user's question, but the answer itself MUST come
   only from the uploaded document context.

9. If the user's question asks about information that
   is not present in the uploaded documents, do not answer
   using your general knowledge.

---------------------------------------------------------
PREVIOUS CONVERSATION
---------------------------------------------------------

{history_text}

---------------------------------------------------------
DOCUMENT CONTEXT
---------------------------------------------------------

{context}

---------------------------------------------------------
CURRENT QUESTION
---------------------------------------------------------

{question}

---------------------------------------------------------
ANSWER
---------------------------------------------------------
"""


    # -----------------------------------------------------
    # 10. Call Ollama
    # -----------------------------------------------------

    try:

        response = await model.ainvoke(
            prompt
        )

    except Exception as e:

        print(
            f"LLM error: {e}"
        )

        return {
            "answer": (
                "There was an error while "
                "generating the answer."
            ),
            "sources": [],
        }


    # -----------------------------------------------------
    # 11. Extract answer
    # -----------------------------------------------------

    answer = response.content


    # Handle unusual response formats
    if not isinstance(
        answer,
        str,
    ):

        answer = str(
            answer
        )


    answer = answer.strip()


    # -----------------------------------------------------
    # 12. Detect "information not found"
    # -----------------------------------------------------

    normalized_answer = (
        answer
        .strip()
        .lower()
        .replace(
            '"',
            "",
        )
        .replace(
            "'",
            "",
        )
    )


    normalized_fallback = (
        FALLBACK_ANSWER
        .strip()
        .lower()
        .replace(
            '"',
            "",
        )
        .replace(
            "'",
            "",
        )
    )


    # -----------------------------------------------------
    # 13. If information was not found,
    #     return NO sources
    # -----------------------------------------------------

    if (
        normalized_answer
        == normalized_fallback
    ):

        return {
            "answer": FALLBACK_ANSWER,
            "sources": [],
        }


    # Also handle cases where Ollama adds
    # a small amount of extra text around
    # the fallback response.

    if (
        normalized_fallback
        in normalized_answer
        and len(normalized_answer) < 250
    ):

        return {
            "answer": FALLBACK_ANSWER,
            "sources": [],
        }


    # -----------------------------------------------------
    # 14. Build clean sources
    # -----------------------------------------------------

    sources = []

    seen_sources = set()


    for document, score in filtered_results:

        source = document.metadata.get(
            "source",
            "Unknown",
        )

        page = document.metadata.get(
            "page",
            "Unknown",
        )

        chunk_id = document.metadata.get(
            "chunk_id",
            "Unknown",
        )


        # ---------------------------------------------
        # Normalize source and page
        # ---------------------------------------------

        normalized_source = str(
            source
        ).strip().lower()

        normalized_page = str(
            page
        ).strip().lower()


        # ---------------------------------------------
        # Source + page is treated as one location
        # ---------------------------------------------

        source_key = (
            normalized_source,
            normalized_page,
        )


        # ---------------------------------------------
        # Skip duplicate source locations
        # ---------------------------------------------

        if source_key in seen_sources:

            continue


        seen_sources.add(
            source_key
        )


        # ---------------------------------------------
        # Add source
        # ---------------------------------------------

        sources.append(
            {
                "source": source,
                "page": page,
                "chunk_id": chunk_id,
            }
        )


    # -----------------------------------------------------
    # 15. Return final response
    # -----------------------------------------------------

    return {
        "answer": answer,
        "sources": sources,
    }