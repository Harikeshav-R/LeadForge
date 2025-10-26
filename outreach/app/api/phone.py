import json
import uuid

from fastapi import WebSocket, APIRouter, Depends, Query
from loguru import logger
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse

from app import schemas, crud, Config
from app.core import get_db
from app.tools import phone_call

router = APIRouter()


@router.post("/")
async def start_call():
    return HTMLResponse(content=open("templates/streams.xml").read(), media_type="application/xml")


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, session_id: uuid.UUID = Query(...), db: Session = Depends(get_db)):
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

    state: schemas.State = schemas.State.model_validate(crud.read_state(db, session_id))

    await phone_call(
        websocket,
        stream_sid,
        call_sid,
        account_sid,
        auth_token,
        state.client_name,
        state.website_critique
    )
