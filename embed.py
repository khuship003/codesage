import chromadb
from chromadb.utils import embedding_functions
from ingest import main as get_chunks

# This uses a free, local model to turn text into embeddings
# (runs on your own laptop, no API call needed for this part)
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# Creates (or connects to) a local database folder called "chroma_db"
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Creates (or reuses) a "collection" - think of it like a table in a database
collection = chroma_client.get_or_create_collection(
    name="codesage_chunks",
    embedding_function=embedding_function
)


def build_index():
    chunks = get_chunks()

    # Chroma needs three parallel lists: unique IDs, the actual text, and metadata
    ids = []
    documents = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        ids.append(f"chunk_{i}")
        documents.append(chunk["text"])
        metadatas.append({
            "file": chunk["file"],
            "chunk_index": chunk["chunk_index"]
        })

    # This is the step that actually creates embeddings and stores everything
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    print(f"Indexed {len(chunks)} chunks into ChromaDB.")


if __name__ == "__main__":
    build_index()