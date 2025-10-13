from pypdf import PdfReader
from pathlib import Path

def extract_text_from_pdf(pdf_path: str) -> str:
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    reader = PdfReader(str(path))
    texts = []
    for i, page in enumerate(reader.pages):
        try:
            txt = page.extract_text() or ""
        except Exception:
            txt = ""
        if txt:
            texts.append(f"\n\n--- Page {i+1} ---\n{txt.strip()}")
        else:
            texts.append(f"\n\n--- Page {i+1} ---\n[No text extracted]")
    return "\n".join(texts)
