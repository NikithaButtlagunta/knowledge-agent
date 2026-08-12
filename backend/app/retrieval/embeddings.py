from langchain_huggingface import HuggingFaceEmbeddings


def get_embedding_model():
    """
    Create and return a local embedding model.
    """

    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


if __name__ == "__main__":
    embeddings = get_embedding_model()

    text = "This is a test sentence for our Knowledge Agent."

    vector = embeddings.embed_query(text)

    print("Embedding created successfully!")
    print("Vector dimensions:", len(vector))