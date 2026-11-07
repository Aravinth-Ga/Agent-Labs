from pathlib import Path

DEBUG = False
QUESTION_FILE = "golden/b2_questions.txt"

from loaders import load
from chunker import chunk
from store import get_collection, reset_collection, store_chunks, retrieve_similar_chunks

def load_questions(path: str) -> list[str]:
    """Read one question per line from a text file."""
    question_path = Path(path)
    if not question_path.exists():
        raise FileNotFoundError(f"Question file not found: {question_path}")

    return [line.strip() for line in question_path.read_text(encoding="utf-8").splitlines() if line.strip()]

def verify_no_duplicate_indexing():
    """Index the same chunks twice and verify the collection count stays stable."""
    documents = load("docs")
    chunks = chunk(documents)
    collection_name = "docs"

    reset_collection(collection_name)
    store_chunks(chunks, collection_name=collection_name)
    first_count = get_collection(collection_name).count()
    print(f"[verify] first run count: {first_count}")

    store_chunks(chunks, collection_name=collection_name)
    second_count = get_collection(collection_name).count()
    print(f"[verify] second run count: {second_count}")

    if first_count == second_count:
        print(f"[verify] pass: count stayed the same ({first_count}) — no duplicates added")
    else:
        print(f"[verify] fail: counts differ ({first_count} vs {second_count})")

    return first_count, second_count


def run_retrieval_check(question_file: str = QUESTION_FILE, top_k: int = 3):
    """Load docs, index them, and test the VIN/NvM questions against the stored vector index."""
    documents = load("docs")
    chunks = chunk(documents)
    collection_name = "docs"

    reset_collection(collection_name)
    store_chunks(chunks, collection_name=collection_name)

    questions = load_questions(question_file)
    print(f"[retrieval] testing {len(questions)} questions from {question_file}")

    for index, question in enumerate(questions, start=1):
        matches = retrieve_similar_chunks(question, top_k=top_k, collection_name=collection_name)
        print(f"\n--- Q{index}: {question} ---")

        if not matches:
            print("[retrieval] no matches found")
            continue

        for match in matches:
            text = " ".join(match["text"].split())
            print(f"[score={match['score']:.4f}] {match['file']} | page {match['page']} | {text[:220]}")

    return questions


if __name__ == "__main__":
    run_retrieval_check()
    if DEBUG:
        verify_no_duplicate_indexing()
