from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    GOOGLE_API_KEY: str
    SUPABASE_DB_URL: str
    MAPMYINDIA_CLIENT_ID: str
    MAPMYINDIA_CLIENT_SECRET: str
    DATA_PATH: str = "data/"
    OUTPUT_PATH: str = "output/"
    PROMPTS_PATH: str = "prompts/"
    PROCESSED_PATH: str = "processed/"

    class Config:
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Auto-create necessary folders
        for folder in [self.DATA_PATH, self.OUTPUT_PATH, self.PROMPTS_PATH]:
            os.makedirs(folder, exist_ok=True)

try:
    settings = Settings()
except Exception as e:
    raise RuntimeError(f"Error loading settings: {e}")