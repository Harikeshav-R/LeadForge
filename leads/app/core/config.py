import os

class Config:
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY")

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    MODEL_NAME: str = os.getenv("MODEL_NAME")
    MODEL_PROVIDER: str = os.getenv("MODEL_PROVIDER")
