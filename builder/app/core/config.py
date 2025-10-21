import os


class Config:
    DEBUG: bool = os.getenv("DEBUG") == "true"

    DATABASE_URL: str = os.getenv("DATABASE_URL")

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    MODEL_NAME: str = os.getenv("MODEL_NAME")
    MODEL_PROVIDER: str = os.getenv("MODEL_PROVIDER")
