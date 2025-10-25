import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router
from app.config import Config
from app.database import Base, engine

Base.metadata.create_all(bind=engine)


# --- Lifespan Event Handler (Startup) ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(Config.DEPLOYED_SITES_DIR, exist_ok=True)
    print(f"Server startup complete. Hosting sites from: {os.path.abspath(Config.DEPLOYED_SITES_DIR)}")
    yield

    # Code below yield runs on shutdown (e.g., cleanup)
    print("Server shutting down.")


app = FastAPI(lifespan=lifespan)

app.include_router(router)

if Config.DEBUG:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],  # Allows all standard HTTP methods (GET, POST, PUT, DELETE, etc.)
        allow_headers=["*"],  # Allows all headers in the request
    )
