import json
import os

from fastapi import WebSocket, APIRouter, Depends
from loguru import logger
from starlette.responses import HTMLResponse

from app.tools import phone_call

router = APIRouter()


@router.post("/")
async def start_call():
    return HTMLResponse(content=open("templates/streams.xml").read(), media_type="application/xml")


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    start_data = websocket.iter_text()
    await start_data.__anext__()
    call_data = json.loads(await start_data.__anext__())

    logger.info(call_data)

    stream_sid = call_data["start"]["streamSid"]
    call_sid = call_data["start"]["callSid"]
    account_sid = call_data["start"]["accountSid"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]

    logger.success("WebSocket connection accepted")

    await phone_call(websocket, stream_sid, call_sid, account_sid, auth_token)
