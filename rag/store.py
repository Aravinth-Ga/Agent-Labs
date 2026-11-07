import os
import shutil
import chromadb

from chunker import chunk
from embedder import MODEL_NAME, embed


CHROMA_DB_PATH = "rag/store"
BATCH_SIZE = 500

# Create a single persistent client for the local vector database.
vector_db_store_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)


def reset_database():
    """Delete the on-disk ChromaDB directory so the collection is rebuilt from scratch."""
    global vector_db_store_client

    try:
        if hasattr(vector_db_store_client, "_client"):
            vector_db_store_client._client.close()
    except Exception:
        pass

    try:
        if hasattr(vector_db_store_client, "close"):
            vector_db_store_client.close()
    except Exception:
        pass

    if os.path.exists(CHROMA_DB_PATH):
        shutil.rmtree(CHROMA_DB_PATH)
        print(f"[store] removed persistent DB at {CHROMA_DB_PATH}")

    vector_db_store_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    return vector_db_store_client

def reset_collection(collection_name="docs"):
    """Delete the selected collection and rebuild the database from scratch."""
    reset_database()
    return get_collection(collection_name)

def get_collection(collection_name="docs"):
    """Create or reuse the vector store for chunk retrieval."""
    return vector_db_store_client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine", "embed_model": MODEL_NAME},
    )


def store_chunks(chunks: list[chunk], collection_name="docs"):
    """Embed chunk text and save it to ChromaDB."""
    collection = get_collection(collection_name)
    chunk_texts = [chunk_item.text for chunk_item in chunks]
    embeddings = embed(chunk_texts)

    for i in range(0, len(chunks), BATCH_SIZE):
        #create batch of chunks and embedding vector to upsert at the same time
        batch_chunks = chunks[i:i + BATCH_SIZE]
        batch_embeddings = embeddings[i:i + BATCH_SIZE]

        # upsert the data into ChromaDB (ids, vectors, documents and metadata)
        collection.upsert(
            ids=[f"{chunk.file}:{chunk.page}:{chunk.idx}" for chunk in batch_chunks],
            embeddings=batch_embeddings.tolist(),
            documents=[chunk.text for chunk in batch_chunks],
            metadatas=[{"file": chunk.file, "page": chunk.page} for chunk in batch_chunks],
        )

    #print(f"[store] {collection.count()} chunks in '{collection_name}'")
    return collection

def retrieve_similar_chunks(question: str, top_k=5, collection_name="docs") -> list[dict]:
    """Embed a question and return the closest matching chunks from the vector store."""
    collection = get_collection(collection_name)

    # Convert the user question into a vector using the same embedding model.
    question_vector = embed([question])[0].tolist()

    # Search the stored vectors for the nearest neighbors.
    search_results = collection.query(
        query_embeddings=[question_vector],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    matches = []
    # Build a clean output list with text, source file, page, and similarity score.
    for document, metadata, distance in zip(search_results["documents"][0], search_results["metadatas"][0], search_results["distances"][0]):   
        matches.append(
            {
                "text": document,
                "file": metadata["file"],
                "page": metadata["page"],
                "score": 1 - distance,
            }
        )

    
    return matches


