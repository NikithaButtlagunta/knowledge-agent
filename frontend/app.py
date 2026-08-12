import streamlit as st
import requests


# =========================================================
# CONFIGURATION
# =========================================================

BACKEND_URL = "http://127.0.0.1:8000"


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Knowledge Agent",
    page_icon="📚",
    layout="wide",
)


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# =========================================================
# HELPER FUNCTION
# =========================================================

def get_unique_sources(sources):
    """
    Remove duplicate source locations.

    A source is considered unique based on:
        source filename + page number

    Filename comparison is case-insensitive.
    """

    unique_sources = []
    seen_sources = set()

    for source in sources:

        if not isinstance(source, dict):
            continue

        source_name = str(
            source.get(
                "source",
                "Unknown"
            )
        ).strip().lower()

        page = str(
            source.get(
                "page",
                "Unknown"
            )
        ).strip().lower()

        source_key = (
            source_name,
            page
        )

        if source_key in seen_sources:
            continue

        seen_sources.add(
            source_key
        )

        unique_sources.append(
            source
        )

    return unique_sources


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("📚 Knowledge Agent")

    st.caption(
        "Upload documents and ask questions "
        "using AI-powered document retrieval."
    )


    # =====================================================
    # DOCUMENT MANAGEMENT
    # =====================================================

    st.header("📄 Document Management")


    # -----------------------------------------------------
    # PDF UPLOAD
    # -----------------------------------------------------

    uploaded_file = st.file_uploader(
        "Upload a PDF",
        type=["pdf"],
        help="Upload a PDF document to your knowledge base.",
    )


    if uploaded_file is not None:

        st.write(
            f"Selected: **{uploaded_file.name}**"
        )


        if st.button(
            "📤 Upload PDF",
            use_container_width=True,
        ):

            try:

                with st.spinner(
                    "Uploading and processing PDF..."
                ):

                    response = requests.post(
                        f"{BACKEND_URL}/upload",

                        files={
                            "file": (
                                uploaded_file.name,
                                uploaded_file.getvalue(),
                                "application/pdf",
                            )
                        },

                        timeout=300,
                    )


                # -------------------------------------------------
                # SUCCESSFUL HTTP RESPONSE
                # -------------------------------------------------

                if response.status_code == 200:

                    data = response.json()


                    if data.get(
                        "success",
                        False,
                    ):

                        st.success(
                            data.get(
                                "message",
                                "PDF uploaded successfully.",
                            )
                        )

                        st.rerun()


                    else:

                        st.warning(
                            data.get(
                                "message",
                                "Upload failed.",
                            )
                        )


                else:

                    st.error(
                        f"Upload failed. "
                        f"Status code: "
                        f"{response.status_code}"
                    )


                    try:

                        st.json(
                            response.json()
                        )

                    except Exception:

                        st.text(
                            response.text
                        )


            except requests.exceptions.ConnectionError:

                st.error(
                    "❌ Could not connect to the backend."
                )

                st.info(
                    "Make sure FastAPI is running on "
                    "http://127.0.0.1:8000"
                )


            except requests.exceptions.Timeout:

                st.error(
                    "⏳ Upload timed out. "
                    "The PDF may take too long to process."
                )


            except Exception as e:

                st.error(
                    f"❌ Upload error: {str(e)}"
                )


    # =====================================================
    # DOCUMENT LIST
    # =====================================================

    st.divider()

    st.subheader("📚 Uploaded Documents")


    # -----------------------------------------------------
    # REFRESH DOCUMENTS
    # -----------------------------------------------------

    if st.button(
        "🔄 Refresh Documents",
        use_container_width=True,
    ):

        st.rerun()


    # -----------------------------------------------------
    # GET DOCUMENTS
    # -----------------------------------------------------

    try:

        documents_response = requests.get(
            f"{BACKEND_URL}/documents",
            timeout=60,
        )


        if documents_response.status_code == 200:

            documents_data = (
                documents_response.json()
            )


            documents = documents_data.get(
                "documents",
                [],
            )


            # -------------------------------------------------
            # DOCUMENTS EXIST
            # -------------------------------------------------

            if documents:

                for document in documents:

                    if not isinstance(
                        document,
                        dict,
                    ):

                        continue


                    document_name = document.get(
                        "source",
                        document.get(
                            "filename",
                            "Unknown document",
                        ),
                    )


                    doc_id = document.get(
                        "doc_id"
                    )


                    # -----------------------------------------
                    # Document row
                    # -----------------------------------------

                    col1, col2 = st.columns(
                        [4, 1]
                    )


                    with col1:

                        st.write(
                            f"📄 {document_name}"
                        )


                    # -----------------------------------------
                    # DELETE DOCUMENT
                    # -----------------------------------------

                    with col2:

                        if st.button(
                            "🗑️",
                            key=f"delete_{doc_id}",
                            help=f"Delete {document_name}",
                        ):

                            if not doc_id:

                                st.error(
                                    "Document ID is missing."
                                )

                            else:

                                try:

                                    with st.spinner(
                                        "Deleting..."
                                    ):

                                        delete_response = (
                                            requests.delete(
                                                f"{BACKEND_URL}/documents/{doc_id}",
                                                timeout=60,
                                            )
                                        )


                                    if (
                                        delete_response.status_code
                                        == 200
                                    ):

                                        delete_data = (
                                            delete_response.json()
                                        )


                                        if delete_data.get(
                                            "success",
                                            False,
                                        ):

                                            st.success(
                                                "Document deleted successfully."
                                            )

                                            st.rerun()


                                        else:

                                            st.error(
                                                delete_data.get(
                                                    "message",
                                                    "Could not delete document.",
                                                )
                                            )


                                    else:

                                        st.error(
                                            f"Delete failed. "
                                            f"Status code: "
                                            f"{delete_response.status_code}"
                                        )


                                except requests.exceptions.ConnectionError:

                                    st.error(
                                        "❌ Could not connect "
                                        "to the backend."
                                    )


                                except requests.exceptions.Timeout:

                                    st.error(
                                        "⏳ Delete request timed out."
                                    )


                                except Exception as e:

                                    st.error(
                                        f"❌ Delete error: {str(e)}"
                                    )


            else:

                st.info(
                    "No documents uploaded yet."
                )


        else:

            st.warning(
                "Could not load documents."
            )


    except requests.exceptions.ConnectionError:

        st.warning(
            "⚠️ Backend is not running."
        )


    except Exception as e:

        st.warning(
            f"Could not load documents: {str(e)}"
        )


    # =====================================================
    # CHAT CONTROLS
    # =====================================================

    st.divider()

    st.subheader("💬 Chat Controls")


    # -----------------------------------------------------
    # CLEAR CHAT
    # -----------------------------------------------------

    if st.session_state.messages:

        if st.button(
            "🗑️ Clear Chat",
            use_container_width=True,
        ):

            st.session_state.messages = []

            st.rerun()

    else:

        st.caption(
            "No conversation to clear."
        )


# =========================================================
# MAIN PAGE
# =========================================================

st.title("📚 Knowledge Agent")

st.caption(
    "Ask questions about your uploaded documents."
)


# =========================================================
# CHAT HISTORY DISPLAY
# =========================================================

for message in st.session_state.messages:

    role = message.get(
        "role",
        "assistant",
    )

    content = message.get(
        "content",
        "",
    )


    with st.chat_message(role):

        st.markdown(content)


        # =================================================
        # SOURCES FOR PREVIOUS MESSAGES
        # =================================================

        if role == "assistant":

            sources = message.get(
                "sources",
                [],
            )


            if sources:

                # -----------------------------------------
                # REMOVE DUPLICATES
                # -----------------------------------------

                unique_sources = get_unique_sources(
                    sources
                )


                # -----------------------------------------
                # DISPLAY SOURCES
                # -----------------------------------------

                if unique_sources:

                    with st.expander(
                        f"📚 Sources ({len(unique_sources)})"
                    ):

                        for source in unique_sources:

                            source_name = source.get(
                                "source",
                                "Unknown",
                            )

                            page = source.get(
                                "page",
                                "Unknown",
                            )

                            chunk_id = source.get(
                                "chunk_id",
                                "Unknown",
                            )


                            st.markdown(
                                f"""
**📄 {source_name}**

Page: **{page}**  
Chunk: `{chunk_id}`
"""
                            )

                            st.divider()


# =========================================================
# CHAT INPUT
# =========================================================

question = st.chat_input(
    "Ask a question about your documents..."
)


# =========================================================
# PROCESS QUESTION
# =========================================================

if question:

    # =====================================================
    # 1. BUILD PREVIOUS CONVERSATION HISTORY
    # =====================================================

    history = []


    for message in st.session_state.messages:

        history.append(
            {
                "role": message.get(
                    "role",
                    "",
                ),

                "content": message.get(
                    "content",
                    "",
                ),
            }
        )


    # =====================================================
    # 2. DISPLAY USER QUESTION
    # =====================================================

    with st.chat_message("user"):

        st.markdown(question)


    # =====================================================
    # 3. ASK BACKEND
    # =====================================================

    try:

        with st.chat_message("assistant"):

            with st.spinner(
                "🔎 Searching your documents..."
            ):

                response = requests.post(
                    f"{BACKEND_URL}/chat",

                    json={
                        "question": question,
                        "history": history,
                    },

                    timeout=300,
                )


            # =================================================
            # 4. SUCCESSFUL RESPONSE
            # =================================================

            if response.status_code == 200:

                data = response.json()


                # ---------------------------------------------
                # ANSWER
                # ---------------------------------------------

                answer = data.get(
                    "answer",
                    "No answer received.",
                )


                # ---------------------------------------------
                # SOURCES
                # ---------------------------------------------

                sources = data.get(
                    "sources",
                    [],
                )


                # ---------------------------------------------
                # DISPLAY ANSWER
                # ---------------------------------------------

                st.markdown(answer)


                # ---------------------------------------------
                # REMOVE DUPLICATE SOURCES
                # ---------------------------------------------

                unique_sources = get_unique_sources(
                    sources
                )


                # ---------------------------------------------
                # DISPLAY SOURCES
                # ---------------------------------------------

                if unique_sources:

                    with st.expander(
                        f"📚 Sources ({len(unique_sources)})"
                    ):

                        for source in unique_sources:

                            source_name = source.get(
                                "source",
                                "Unknown",
                            )

                            page = source.get(
                                "page",
                                "Unknown",
                            )

                            chunk_id = source.get(
                                "chunk_id",
                                "Unknown",
                            )


                            st.markdown(
                                f"""
**📄 {source_name}**

Page: **{page}**  
Chunk: `{chunk_id}`
"""
                            )

                            st.divider()


                # =================================================
                # SAVE USER MESSAGE
                # =================================================

                st.session_state.messages.append(
                    {
                        "role": "user",
                        "content": question,
                    }
                )


                # =================================================
                # SAVE ASSISTANT MESSAGE
                # =================================================

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,

                        # Save original sources so the
                        # backend data is preserved.
                        "sources": sources,
                    }
                )


            # =================================================
            # BACKEND ERROR
            # =================================================

            else:

                st.error(
                    f"Backend returned status code "
                    f"{response.status_code}"
                )


                try:

                    st.json(
                        response.json()
                    )

                except Exception:

                    st.text(
                        response.text
                    )


    # =====================================================
    # CONNECTION ERROR
    # =====================================================

    except requests.exceptions.ConnectionError:

        st.error(
            "❌ Could not connect to the backend."
        )

        st.info(
            "Make sure FastAPI is running with:"
        )

        st.code(
            "uvicorn backend.app.main:app --reload"
        )


    # =====================================================
    # TIMEOUT
    # =====================================================

    except requests.exceptions.Timeout:

        st.error(
            "⏳ The request timed out. "
            "The document processing or AI response "
            "took too long."
        )


    # =====================================================
    # OTHER ERROR
    # =====================================================

    except Exception as e:

        st.error(
            f"❌ Error: {str(e)}"
        )