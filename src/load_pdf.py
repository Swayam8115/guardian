import pdfplumber
from pathlib import Path

def extract_text_from_pdf(pdf_path: str) -> str:
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    texts = []
    with pdfplumber.open(str(path)) as pdf:
        for i, page in enumerate(pdf.pages):
            try:
                txt = page.extract_text() or ""
            except:
                txt = ""
            
            texts.append(
                f"\n\n--- Page {i+1} ---\n{txt.strip() if txt else '[No text extracted]'}"
            )
    return "\n".join(texts)
