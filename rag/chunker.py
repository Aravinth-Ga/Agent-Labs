from dataclasses import dataclass
from loaders import load

DEBUG = False

@dataclass
class Chunk:
    text: str
    file: str
    page:int
    idx:int

# Take the text and remove empty lines.
def get_non_empty_lines(text):
    return [line for line in text.splitlines() if line.strip()]

# Split documents into chunks using sentence boundaries whenever possible.
# We use the character limit as a soft target, not a hard cut in the middle of a sentence.
def chunk(documents, size_chars=1600, overlap_char=240):
    chunks = []

    # Go through each document one by one.
    for document in documents:
        if not document.text:
            continue

        # Start with cleaned lines.
        lines = get_non_empty_lines(document.text)
        sentence_parts = []

        # Break each line into sentence-like pieces.
        for line in lines:
            for sentence in line.replace("!", ".").replace("?", ".").split("."):
                sentence = sentence.strip()
                if sentence:
                    sentence_parts.append(sentence)

        current_chunk_sentences = []
        current_chunk_size = 0

        # Keep adding sentences until we are close to the target size.
        for sentence in sentence_parts:
            next_size = current_chunk_size + len(sentence) + 1

            if current_chunk_sentences and next_size > size_chars:
                chunk_text = ". ".join(current_chunk_sentences) + "."
                new_chunk = Chunk(chunk_text, document.file, document.page, len(chunks))
                chunks.append(new_chunk)

                # Keep overlap by reusing the last sentence(s) from the current chunk.
                overlap_sentences = []
                overlap_size = 0
                while current_chunk_sentences and overlap_size < overlap_char:
                    last_sentence = current_chunk_sentences.pop()
                    overlap_sentences.insert(0, last_sentence)
                    overlap_size += len(last_sentence) + 1

                current_chunk_sentences = overlap_sentences
                current_chunk_size = overlap_size

            current_chunk_sentences.append(sentence)
            current_chunk_size = sum(len(s) + 1 for s in current_chunk_sentences)

        # Save the final remaining chunk.
        if current_chunk_sentences:
            chunk_text = ". ".join(current_chunk_sentences) + "."
            new_chunk = Chunk(chunk_text, document.file, document.page, len(chunks))
            chunks.append(new_chunk)

    if DEBUG:
        print(f"[chunk] {len(chunks)} chunks created")

        max_chunk_size = max((len(chunk.text) for chunk in chunks), default=0)
        print(f"[chunk] max chunk size: {max_chunk_size} chars")

    return chunks


if __name__ == "__main__":
    chunk(load('docs'))