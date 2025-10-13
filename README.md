# FIR Translator & Structured Extractor (LangChain + Gemini/Groq)

This tool reads an FIR PDF (any language), translates to English, and produces a structured JSON
using a Pydantic schema — powered by LangChain's `with_structured_output`.

## Quick Start

### 1) Install dependencies
```bash
python -m venv .venv && source .venv/bin/activate   # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
