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
def load_pdf(p: Path) -> list[Doc]:
    out = []
    try:
        reader = PdfReader(str(p))
        for i, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()    # Extract can return None aslo hence add " "
            if text:
                out.append(Doc(text, p.name, i))
    except Exception as e:
        print(f"[load] skipped PDF {p.name}: {e}")

    return out

# Read one text file and return it as one Doc.
def load_text(p: Path) -> list[Doc]:
    return [Doc(p.read_text(encoding="utf-8", errors="replace"), p.name, 0)]

# Match each file extension to the correct loader.
LOADERS = {".pdf": load_pdf, ".md": load_text, ".txt": load_text}

# Load all supported files from a folder.
def load(folder: str) -> list[Doc]:
    docs = []

    # Walk the folder tree and process every matching file.
    for p in sorted(Path(folder).rglob("*")):
        fn = LOADERS.get(p.suffix.lower())
        if fn:
            try:
                docs += fn(p)
            except Exception as e:
                print(f"[load] skipped {p.name}: {e}")

    # Keep track of files that produced no text.
    empty = [d for d in docs if not d.text]

    print(f"[load] {len(docs)} docs, {len(empty)} empty")

    # Show a few empty documents for debugging.
    for d in empty[:10]:
        print(f"[load] EMPTY {d.file} p.{d.page}")

    return docs

# Test code
if __name__ == "__main__":
    data = load('docs')
    print(data[0].text[:300])
