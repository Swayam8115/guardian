from pathlib import Path

def load_prompt(path: str) -> str:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Prompt not found at {path}")
    return p.read_text(encoding="utf-8")
