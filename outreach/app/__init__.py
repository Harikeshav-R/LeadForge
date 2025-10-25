import os

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db

app = FastAPI()

if os.getenv("DEBUG") == "true":
    # CORS Middleware for development
    # This allows the frontend (running on localhost:5173) to communicate with the backend.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],  # Allows the dev frontend
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


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
