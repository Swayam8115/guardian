import json
import shutil
from pathlib import Path
from rich import print
from utils.load_pdf import extract_text_from_pdf
from utils.file_handler import read_prompt
from database.db import SessionLocal
from database.crud import insert_fir_record
from chain.build import build_chain
from src.schema import FIRRecord
from config.settings import settings

def process_all_firs():
    data_folder = Path(settings.DATA_PATH)
    output_folder = Path(settings.OUTPUT_PATH)
    prompt_path = Path(settings.PROMPTS_PATH + "extract_fir_prompt.txt")
    processed_folder = Path(settings.PROCESSED_PATH)
    processed_folder.mkdir(exist_ok=True)

    db = SessionLocal()
    prompt_text = read_prompt(prompt_path)
    chain = build_chain(prompt_text)

    fir_files = list(data_folder.glob("*.pdf"))
    if not fir_files:
        print("No FIR PDFs found in the data folder.")
        return

    print(f"[bold]Found {len(fir_files)} FIR(s) to process...[/bold]")

    for pdf_file in fir_files:
        
        output_path = output_folder / f"{pdf_file.stem}.json"
        if output_path.exists():
            print(f"Skipping {pdf_file.name} — already processed.")
            continue

        print(f"\nProcessing: {pdf_file.name}")
        try:
            document_text = extract_text_from_pdf(str(pdf_file))
            result: FIRRecord = chain.invoke({"document_text": document_text})
            fir_json = result.model_dump()

            output_path.write_text(
                json.dumps(fir_json, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

            insert_fir_record(db, pdf_file.name, fir_json)

            shutil.move(str(pdf_file), processed_folder / pdf_file.name)

            print(f"Saved: {output_path}")
            print({
                "fir_number": result.fir_number,
                "Location": result.location,
                "Generalised Location": result.generalised_location,
                "Crime Categories": result.crime_categories,
            })

        except Exception as e:
            print(f"[red]Error processing {pdf_file.name}: {e}[/red]")

    db.close()
    print("\n[bold]Batch FIR Processing Completed![/bold]")

if __name__ == "__main__":
    process_all_firs()
