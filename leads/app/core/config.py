import os

class Config:
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")