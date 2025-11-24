from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import settings

get_llm=ChatGoogleGenerativeAI(model="gemini-2.5-pro",google_api_key=settings.GOOGLE_API_KEY)