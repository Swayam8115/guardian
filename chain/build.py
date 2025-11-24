from models.llm import get_llm
from src.schema import FIRRecord
from langchain_core.prompts import ChatPromptTemplate

def build_chain(prompt_text: str):
    llm = get_llm.with_structured_output(FIRRecord)
    prompt = ChatPromptTemplate.from_template(prompt_text)
    return prompt | llm