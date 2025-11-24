from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    GOOGLE_API_KEY: str
    DATA_PATH: str = "data/"
    OUTPUT_PATH: str = "output/"
    PROMPTS_PATH: str = "prompts/"
    MAX_RETRIES: int = 0

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