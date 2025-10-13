import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from rich import print
from rich.panel import Panel
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from src.schema import FIRRecord
from src.load_pdf import extract_text_from_pdf
from src.prompt_loader import load_prompt


def build_chain(prompt_text: str):
    """
    Build a LangChain chain that:
    - switches between Gemini (Google) and Groq (xAI/OpenAI-compatible)
    - returns a Pydantic-validated FIRRecord
    """
    provider = os.getenv("PROVIDER", "gemini").lower()

    if provider == "groq":
        model_id = os.getenv("GROQ_MODEL", "llama-3.1-70b-instruct")
        llm = ChatGroq(
            model=model_id,
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.1,
        ).with_structured_output(FIRRecord)

    else:  # default = Gemini
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0.1,
            convert_system_message_to_human=True,
        ).with_structured_output(FIRRecord)

    prompt = ChatPromptTemplate.from_template(prompt_text)
    return prompt | llm


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Extract structured, translated FIR data from a PDF using LangChain + Gemini/Groq."
    )
    parser.add_argument(
        "--pdf",
        type=str,
        default="data/sample_fir.pdf",
        help="Path to the input FIR PDF.",
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="prompts/extract_fir_prompt.md",
        help="Path to the chat prompt template file.",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="fir_output.json",
        help="Path to save the structured JSON output.",
    )
    args = parser.parse_args()

    provider = os.getenv("PROVIDER", "gemini").lower()
    print(Panel.fit(f"[bold]Using Provider[/bold]: {provider.upper()}", border_style="yellow"))

    print(Panel.fit(f"[bold]Reading PDF[/bold]\n{args.pdf}", border_style="cyan"))
    document_text = extract_text_from_pdf(args.pdf)

    print(Panel.fit(f"[bold]Loading Prompt[/bold]\n{args.prompt}", border_style="cyan"))
    prompt_text = load_prompt(args.prompt)

    print(Panel.fit("[bold]Building Chain & Invoking Model[/bold]", border_style="green"))
    chain = build_chain(prompt_text)

    result: FIRRecord = chain.invoke({"document_text": document_text})

    out_path = Path(args.out)
    out_path.write_text(json.dumps(result.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")

    print(Panel.fit(f"[bold]Saved structured output[/bold]\n{out_path}", border_style="magenta"))

    print("\n[bold]Quick peek:[/bold]")
    print({
        "fir_number": result.fir_number,
        "police_station": result.police_station,
        "date_of_incident": result.date_of_incident,
        "sections_invoked": result.sections_invoked,
        "Location": result.location,
    })


if __name__ == "__main__":
    main()
