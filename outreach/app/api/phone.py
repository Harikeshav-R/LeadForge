from fastapi import APIRouter
from starlette.responses import HTMLResponse

router = APIRouter()


@router.post("/")
async def start_call():
    return HTMLResponse(content=open("templates/streams.xml").read(), media_type="application/xml")
