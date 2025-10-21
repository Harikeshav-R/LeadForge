from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.agents.workflow import make_graph
from app.core.config import Config
from app.core.database import get_db
from app.schemas.state import State

app = FastAPI()

if Config.DEBUG:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],  # Allows all standard HTTP methods (GET, POST, PUT, DELETE, etc.)
        allow_headers=["*"],  # Allows all headers in the request
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
