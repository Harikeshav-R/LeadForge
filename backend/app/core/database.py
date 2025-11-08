from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import Config


engine = create_engine(Config.POSTGRES_URL)
SessionLocal = sessionmaker(autoflush=True, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
