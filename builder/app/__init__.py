from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import crud, models, schemas
from app.agents import create_compiled_state_graph
from app.api import api_router
from app.core import Config, Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(api_router)

if Config.DEBUG:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],  # Allows all standard HTTP methods (GET, POST, PUT, DELETE, etc.)
        allow_headers=["*"],  # Allows all headers in the request
    )
