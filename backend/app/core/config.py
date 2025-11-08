import os


class Config:
    DEBUG: bool = os.getenv("DEBUG") == "true"

    POSTGRES_HOST: str = (
        os.environ["POSTGRES_HOST"] if os.getenv("POSTGRES_HOST") is not None else ""
    )
    POSTGRES_PORT: str = (
        os.environ["POSTGRES_PORT"] if os.getenv("POSTGRES_PORT") is not None else ""
    )
    POSTGRES_USER: str = (
        os.environ["POSTGRES_USER"] if os.getenv("POSTGRES_USER") is not None else ""
    )
    POSTGRES_PASSWORD: str = (
        os.environ["POSTGRES_PASSWORD"]
        if os.getenv("POSTGRES_PASSWORD") is not None
        else ""
    )
    POSTGRES_DB: str = (
        os.environ["POSTGRES_DB"] if os.getenv("POSTGRES_DB") is not None else ""
    )

    POSTGRES_URL: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
