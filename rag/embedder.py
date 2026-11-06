from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from loaders import load
from chunker import chunk

DEBUG = False

model_path = "C:\\Users\\Aravi\\.cache\\huggingface\\hub\\models--sentence-transformers--all-MiniLM-L6-v2\\snapshots\\1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
MODEL_NAME = "all-MiniLM-L6-v2"

def embed(text: str) -> np.ndarray:
    # Load the embedding model
    model = SentenceTransformer(model_path)
    # Convert text into vectors
    vectors = model.encode(text, normalize_embeddings=True, batch_size=64)
    return np.asarray(vectors, dtype=np.float32)


def main():
    # Load and split the documents into chunks
    documents = load('docs')
    chunks = chunk(documents)

    texts = [chunk_item.text for chunk_item in chunks]
    vectors = embed(texts)

    if DEBUG:
        print("Total chunks:", len(texts))
        print("Vector shape:", vectors.shape)
        print("First vector sample:", vectors[0][:10])

    # Compare the first two chunks
    sim_1_2 = cosine_similarity(vectors[[0]], vectors[[1]])[0, 0]
    print("Similarity chunk 1 vs chunk 2:", sim_1_2)

    if DEBUG:
        # Print a few chunk texts for inspection
        for i, text in enumerate(texts[:3]):
            print(f"\nChunk {i}: {text[:200]}")


if __name__ == "__main__":
    main()
