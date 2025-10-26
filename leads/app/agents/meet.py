import os
import json
import pathlib
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# --- OAuth configuration ---
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events"
]

BASE_DIR = pathlib.Path(__file__).resolve().parent
CLIENT_SECRET_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"


def get_user_credentials():
    """Return user credentials via OAuth. Handles token refresh and local consent flow."""
    creds = None
    if TOKEN_FILE.exists():
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None
        if not creds:
            if not CLIENT_SECRET_FILE.exists():
                raise RuntimeError(
                    f"Missing {CLIENT_SECRET_FILE}. "
                    f"Download OAuth client JSON from Google Cloud and save as client_secret.json"
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CLIENT_SECRET_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return creds


# --- Initialize Calendar API ---
credentials = get_user_credentials()
calendar_service = build("calendar", "v3", credentials=credentials)
calendar_id = os.getenv("GOOGLE_CALENDAR_CALENDAR_ID", "primary")

# --- FastAPI app ---
app = FastAPI(title="Google Meet API via OAuth", version="1.0")


def create_calendar_event_with_meet(summary, description, start_time, end_time, attendees=None):
    """Creates a Google Calendar event with a Meet link."""
    if attendees is None:
        attendees = []

    try:
        event = {
            "summary": summary,
            "description": description,
            "start": {"dateTime": start_time, "timeZone": "America/New_York"},
            "end": {"dateTime": end_time, "timeZone": "America/New_York"},
            "conferenceData": {
                "createRequest": {
                    "requestId": f"meet-{datetime.now().timestamp()}",
                    "conferenceSolutionKey": {"type": "hangoutsMeet"}
                }
            },
            "attendees": [{"email": a} for a in attendees] if attendees else [],
        }

        created_event = (
            calendar_service.events()
            .insert(
                calendarId=calendar_id,
                body=event,
                conferenceDataVersion=1,
            )
            .execute()
        )

        meet_link = created_event.get("hangoutLink")
        event_link = created_event.get("htmlLink")

        return {
            "success": True,
            "meet_link": meet_link,
            "event_link": event_link,
            "event_id": created_event.get("id"),
        }

    except HttpError as e:
        return {"success": False, "error": str(e)}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/create-meet-test")
def create_meet_test():
    """Test endpoint to create a Google Meet event."""
    try:
        now = datetime.now()
        start_time = (now + timedelta(minutes=5)).astimezone().isoformat()
        end_time = (now + timedelta(minutes=35)).astimezone().isoformat()

        result = create_calendar_event_with_meet(
            summary="Google Meet Test",
            description="This meeting was created through OAuth using FastAPI.",
            start_time=start_time,
            end_time=end_time,
            attendees=[]
        )

        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
