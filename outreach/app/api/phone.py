import uuid
from datetime import timedelta

import requests
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from loguru import logger
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud, schemas
from app.core import Config, get_db
from app.schemas import TwilioRecordingPayload, PhoneAnalysisOutput
from app.tools import transcribe_and_analyze_audio, create_calendar_event_with_meet

router = APIRouter()


@router.post("/")
async def start_call():
    return HTMLResponse(content=open("templates/streams.xml").read(), media_type="application/xml")


@router.post("/recording-webhook/{state_id}")
async def handle_recording_webhook(state_id: uuid.UUID, request: Request, db: Session = Depends(get_db)):
    try:
        form_data = await request.form()

        payload = TwilioRecordingPayload.model_validate(form_data)

    except ValidationError as e:
        logger.error(f"Validation Error: {e}")
        logger.error(f"Raw form data: {dict(await request.form())}")
        return {"status": "error", "message": "Invalid form data"}

    logger.info(f"Received webhook for Call SID: {payload.call_sid}")
    logger.info(f"Recording SID: {payload.recording_sid}")
    logger.info(f"Recording Status: {payload.recording_status}")

    if payload.recording_status == "completed":
        logger.info(f"Downloading recording from: {payload.recording_url}")

        try:
            response = requests.get(
                payload.recording_url,
                auth=(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
            )

            response.raise_for_status()

            result: PhoneAnalysisOutput = transcribe_and_analyze_audio(response.content)
            logger.info(f"Transcription result: {result.model_dump_json(indent=2)}")

            state: schemas.State = schemas.State.model_validate(crud.read_state(db, state_id))

            if result.success and result.client_interested_in_meeting and result.meeting_time:
                create_calendar_event_with_meet(
                    f"Meeting with {state.client_name}",
                    f"Website Development Improvement Meeting with {state.client_name}",
                    result.meeting_time.isoformat(),
                    (result.meeting_time + timedelta(minutes=30)).isoformat(),
                    attendees=[state.client_email, Config.SENDER_EMAIL_ADDRESS]
                )

        except requests.RequestException as e:
            logger.error(f"Error downloading file: {e}")
            # Let Twilio know something went wrong on our end
            raise HTTPException(status_code=500, detail=f"Failed to download recording: {e}")
    else:
        logger.info(f"Recording not yet completed (status: {payload.recording_status}). Skipping download.")

    # Acknowledge the webhook with a 200 OK response
    return {"status": "success", "message": "Webhook received"}
