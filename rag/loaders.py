from dataclasses import dataclass
from pathlib import Path
from pypdf import PdfReader
from openpyxl import load_workbook

# One extracted document chunk.
@dataclass
class Doc:
    text: str
    file: str
    page: int

# Read one PDF and return one Doc per page.
def load_pdf(pdf_path: Path) -> list[Doc]:
    extracted_docs = []
    try:
        reader = PdfReader(str(pdf_path))
        for page_number, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            if text:
                extracted_docs.append(Doc(text, pdf_path.name, page_number))
    except Exception as e:
        print(f"[load] skipped PDF {pdf_path.name}: {e}")

    return extracted_docs

# Read one text file and return it as one Doc.
def load_text(file_path: Path) -> list[Doc]:
    return [Doc(file_path.read_text(encoding="utf-8", errors="replace"), file_path.name, 0)]

# Match each file extension to the correct loader.
LOADERS = {".pdf": load_pdf, ".md": load_text, ".txt": load_text}

# Load all supported files from a folder.
def load(folder_path: str) -> list[Doc]:
    all_docs = []

    # Walk the folder tree and process every matching file.
    for file_path in sorted(Path(folder_path).rglob("*")):
        loader = LOADERS.get(file_path.suffix.lower())
        if loader:
            try:
                all_docs += loader(file_path)
            except Exception as e:
                print(f"[load] skipped {file_path.name}: {e}")

    # Keep track of files that produced no text.
    empty_docs = [doc for doc in all_docs if not doc.text]

    print(f"[load] {len(all_docs)} docs, {len(empty_docs)} empty")

    # Show a few empty documents for debugging.
    for doc in empty_docs[:10]:
        print(f"[load] EMPTY {doc.file} p.{doc.page}")

    return all_docs

# Test code
if __name__ == "__main__":
    loaded_docs = load('docs')
    print(loaded_docs[0].text[:300])
