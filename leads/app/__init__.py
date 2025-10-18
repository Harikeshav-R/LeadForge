from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello World"}


@app.get("/api/db-version")
def get_db_version(db: Session = Depends(get_db)):
    """
    Tests the database connection by retrieving the PostgreSQL version.
    """
    try:
        result = db.execute(text("SELECT version()")).scalar()
        return {"db_version": result}
    except Exception as e:
        return {"error": f"Database connection failed: {e}"}
