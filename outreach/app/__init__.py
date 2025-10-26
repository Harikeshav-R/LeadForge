<<<<<<< HEAD
import json
import uuid

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket
from loguru import logger
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.agents import create_compiled_state_graph
from app.api import api_router
from app.core import Config, Base, engine, get_db
from app.tools import phone_call

Base.metadata.create_all(bind=engine)

app = FastAPI()

if Config.DEBUG:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for testing
=======
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
>>>>>>> main-holder
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

<<<<<<< HEAD
app.include_router(api_router)


@app.websocket("/ws/{state_id}")
async def websocket_endpoint(*, websocket: WebSocket, state_id: uuid.UUID, db: Session = Depends(get_db)):
    await websocket.accept()
    start_data = websocket.iter_text()
    await start_data.__anext__()
    call_data = json.loads(await start_data.__anext__())

    logger.info(call_data)

    stream_sid = call_data["start"]["streamSid"]
    call_sid = call_data["start"]["callSid"]
    account_sid = call_data["start"]["accountSid"]
    auth_token = Config.TWILIO_AUTH_TOKEN

    logger.success("WebSocket connection accepted")

    state: schemas.State = schemas.State.model_validate(crud.read_state(db, state_id))

    await phone_call(
        websocket,
        stream_sid,
        call_sid,
        account_sid,
        auth_token,
        state.client_name,
        state.website_critique
    )
=======

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
>>>>>>> main-holder
