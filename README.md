# Knowledge Agent

An AI-powered document question-answering application that allows users to upload PDF documents and ask questions about their content.

## Features

- PDF upload
- PDF text extraction
- Text chunking
- Document embeddings
- ChromaDB vector database
- Semantic search
- RAG-based question answering
- Llama 3.2 through Ollama
- Conversation history
- Source references
- Duplicate document detection
- Document management

## Technology Stack

- Python
- FastAPI
- Streamlit
- LangChain
- ChromaDB
- Ollama
- Llama 3.2
- Hugging Face Embeddings
- PyPDF

## Architecture

User
↓
Streamlit Frontend
↓
FastAPI Backend
↓
PDF Processing
↓
Embeddings
↓
ChromaDB
↓
Semantic Retrieval
↓
Llama 3.2
↓
Answer + Sources

## How It Works

1. User uploads a PDF.
2. The backend extracts the text.
3. The text is divided into chunks.
4. Embeddings are generated.
5. Chunks are stored in ChromaDB.
6. User asks a question.
7. Relevant chunks are retrieved.
8. Retrieved information is sent to Llama 3.2.
9. The AI generates an answer using the document context.
10. Sources are displayed with the answer.

## Running the Project

### Start the backend

```bash
uvicorn backend.app.main:app --reload