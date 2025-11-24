import json
from pathlib import Path
from rich import print
from models.llm import get_llm
from src.schema import FIRRecord
from config.settings import settings
from utils.file_handler import read_prompt
from src.load_pdf import extract_text_from_pdf
from langchain_core.prompts import ChatPromptTemplate


def build_chain(prompt_text: str):
    llm = get_llm.with_structured_output(FIRRecord)
    prompt = ChatPromptTemplate.from_template(prompt_text)
    return prompt | llm


def main():

    document_text = extract_text_from_pdf(settings.DATA_PATH + "0172 Publish FIR.pdf")
    prompt_text = read_prompt(settings.PROMPTS_PATH + "extract_fir_prompt.txt")
    chain = build_chain(prompt_text)

    result: FIRRecord = chain.invoke({"document_text": document_text})

    out_path = Path(settings.OUTPUT_PATH + "FIR_REPORT")
    out_path.write_text(json.dumps(result.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n[bold]Quick peek:[/bold]")
    print({
        "fir_number": result.fir_number,
        "police_station": result.police_station,
        "date_of_incident": result.date_of_incident,
        "sections_invoked": result.sections_invoked,
        "Location": result.location,
        "Crime Categories": result.crime_categories,
    })


if __name__ == "__main__":
    main()
