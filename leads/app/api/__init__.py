from fastapi import APIRouter

from app.api import lead, state, workflow

api_router = APIRouter(prefix="/api")
api_router.include_router(lead.router, prefix="/lead", tags=["lead"])
api_router.include_router(state.router, prefix="/state", tags=["state"])
api_router.include_router(workflow.router, prefix="/workflow", tags=["workflow"])
