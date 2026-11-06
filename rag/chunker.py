from dataclasses import dataclass
from loaders import load

@dataclass
class Chunk:
    text: str
    file: str
    page:int
    idx:int

# Take the text and remove empty lines.
def get_non_empty_lines(text):
    return [line for line in text.splitlines() if line.strip()]

# Split documents into fixed-size chunks with overlapping context.
# Default values are roughly 400 tokens (~1600 chars) with a 60-token overlap (~240 chars).
def chunk(documents, size_chars=1600, overlap_char=240):
    chunks = []

    # Go through each document one by one.
    for document in documents:
        if not document.text:
            continue

        # Remove empty lines first.
        lines = get_non_empty_lines(document.text)
        current_chunk_lines, current_chunk_size = [], 0

        # Keep adding lines until the part is big enough.
        for line_index, current_line in enumerate(lines):
            current_chunk_lines.append(current_line)
            current_chunk_size += len(current_line) + 1

            # Save this chunk if it is large enough or if it is the last part.
            if current_chunk_size >= size_chars or line_index == len(lines) - 1:
                chunk_text = "\n".join(current_chunk_lines)
                new_chunk = Chunk(chunk_text, document.file, document.page, len(chunks))
                chunks.append(new_chunk)

                # Keep the ending lines as overlap for the next chunk.
                overlap_lines = []
                overlap_size = 0

                while current_chunk_lines and overlap_size < overlap_char:
                    last_line = current_chunk_lines.pop()
                    overlap_lines.insert(0, last_line)
                    overlap_size += len(last_line) + 1

                current_chunk_lines = overlap_lines
                current_chunk_size = overlap_size

    # Print a small summary for debugging.
    for chunk_item in chunks:
        print(f"[Chunk {chunk_item.text}] {chunk_item.file} page {chunk_item.page} -> {len(chunk_item.text)} chars\n\n")

    print(f"[chunk] {len(chunks)} chunks from {len(chunks)} documents")

    # Debug code to print max chunk size
    max_chunk_size = max((len(chunk.text) for chunk in chunks), default=0)
    print(f"[Max Chunk size is] {max_chunk_size}")

    return chunks


if __name__ == "__main__":
    chunk(load('docs'))