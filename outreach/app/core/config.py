import os


class Config:
    DEBUG: bool = os.getenv("DEBUG") == "true"

    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB: str = os.getenv("POSTGRES_OUTREACH_DB")

    POSTGRES_URL: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    MODEL_NAME: str = os.getenv("MODEL_NAME")
    MODEL_PROVIDER: str = os.getenv("MODEL_PROVIDER")

    SENDER_EMAIL_ADDRESS: str = os.getenv("SENDER_EMAIL_ADDRESS")
    SENDER_EMAIL_PASSWORD: str = os.getenv("SENDER_EMAIL_PASSWORD")

    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER")

    BASE_WS_URL: str = os.getenv("BASE_WS_URL")
