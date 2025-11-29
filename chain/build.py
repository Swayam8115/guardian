from models.llm import get_llm
from src.schema import FIRRecord
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import HumanMessage

def build_chain(prompt_text: str):
    llm = get_llm.with_structured_output(FIRRecord)

    def assemble(input_data):

        pdf_bytes = input_data["pdf"]

        msg = HumanMessage(content=[
            {"type": "text", "text": prompt_text},
            {
                "type": "media",
                "mime_type": "application/pdf",
                "data": pdf_bytes
            }
        ])

        return [msg]

    return RunnableLambda(assemble) | llm