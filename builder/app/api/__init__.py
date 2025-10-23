from fastapi import APIRouter

from app.api import state, workflow

api_router = APIRouter()
api_router.include_router(state.router, prefix="/state", tags=["state"])
api_router.include_router(workflow.router, prefix="/workflow", tags=["workflow"])
