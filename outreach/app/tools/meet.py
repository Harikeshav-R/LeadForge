import os
import pathlib
from datetime import datetime, timedelta
from typing import Optional, Any

import google.auth.exceptions
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from loguru import logger

# --- Module-level configuration ---
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
DEFAULT_CLIENT_SECRET_FILE = BASE_DIR / "credentials.json"
DEFAULT_TOKEN_FILE = BASE_DIR / "token.json"
DEFAULT_SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events"
]


class GoogleCalendarClient:
    """A client for interacting with the Google Calendar API.

    Handles OAuth authentication, token management, and provides methods
    for creating calendar events with Google Meet links.

    Attributes:
        client_secret_file (pathlib.Path): Path to the client secret JSON.
        token_file (pathlib.Path): Path to store/read the token JSON.
        scopes (list[str]): list of Google API scopes.
        calendar_id (str): The calendar ID to use (e.g., 'primary').
        credentials (Credentials): The authenticated Google OAuth2 credentials.
        calendar_service (Resource): The built Google Calendar API service object.
    """

    def __init__(
            self,
            client_secret_file: pathlib.Path = DEFAULT_CLIENT_SECRET_FILE,
            token_file: pathlib.Path = DEFAULT_TOKEN_FILE,
            scopes: list[str] = DEFAULT_SCOPES,
            calendar_id: Optional[str] = None
    ) -> None:
        """Initializes the client, authenticates, and builds the service.

        Args:
            client_secret_file: Path to the client secret JSON.
            token_file: Path to store/read the token JSON.
            scopes: list of Google API scopes.
            calendar_id: The calendar ID to use. Defaults to
                env var 'GOOGLE_CALENDAR_CALENDAR_ID' or 'primary'.

        Raises:
            Exception: If authentication or service building fails.
        """
        self.client_secret_file = client_secret_file
        self.token_file = token_file
        self.scopes = scopes
        self.calendar_id = calendar_id or os.getenv("GOOGLE_CALENDAR_CALENDAR_ID", "primary")

        logger.info(
            f"Initializing GoogleCalendarClient for calendar ID: {self.calendar_id}"
        )

        try:
            # Authenticate and build the service upon instantiation
            self.credentials = self._authenticate()
            self.calendar_service: Resource = build(
                "calendar", "v3", credentials=self.credentials
            )
            logger.info("Google Calendar client initialized successfully.")
        except Exception as e:
            logger.critical(
                f"Failed to initialize GoogleCalendarClient: {e}", exc_info=True
            )
            raise

    def _authenticate(self) -> Credentials:
        """Handles the OAuth 2.0 flow.

        1. Loads existing credentials from token_file.
        2. Refreshes expired credentials.
        3. Runs the local server flow if no valid credentials exist.
        4. Saves new/refreshed credentials to token_file.

        Returns:
            Valid user credentials.

        Raises:
            RuntimeError: If the client_secret_file is missing when needed.
            Exception: For other errors during the auth flow.
        """
        creds: Optional[Credentials] = None
        try:
            if self.token_file.exists():
                logger.info(f"Loading credentials from {self.token_file}")
                creds = Credentials.from_authorized_user_file(
                    str(self.token_file), self.scopes
                )
        except (IOError, ValueError) as e:
            logger.warning(
                f"Failed to load token file {self.token_file}: {e}. Will re-authenticate."
            )
            creds = None

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired credentials...")
                try:
                    creds.refresh(Request())
                except google.auth.exceptions.RefreshError as e:
                    logger.warning(
                        f"Failed to refresh token: {e}. Re-authenticating..."
                    )
                    creds = None  # Force re-authentication
                except Exception as e:
                    logger.error(
                        f"An unexpected error occurred during token refresh: {e}. "
                        "Re-authenticating...", exc_info=True
                    )
                    creds = None

            if not creds:
                if not self.client_secret_file.exists():
                    logger.error(
                        f"Missing client secret file: {self.client_secret_file}"
                    )
                    raise RuntimeError(
                        f"Missing {self.client_secret_file}. "
                        f"Download OAuth client JSON from Google Cloud "
                        f"and save as credentials.json"
                    )

                logger.info(
                    f"No valid credentials found. Running local auth flow using {self.client_secret_file}"
                )
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.client_secret_file), self.scopes
                    )
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    logger.critical(f"Local auth flow failed: {e}", exc_info=True)
                    raise

            try:
                # Save the credentials for the next run
                with open(self.token_file, "w") as token:
                    token.write(creds.to_json())
                logger.info(f"Credentials saved to {self.token_file}")
            except IOError as e:
                logger.error(f"Failed to save token file {self.token_file}: {e}")

        return creds

    def create_calendar_event_with_meet(
            self,
            summary: str,
            description: str,
            start_time: str,
            end_time: str,
            attendees: Optional[list[str]] = None,
            time_zone: str = "America/New_York"
    ) -> dict[str, Any]:
        """Creates a Google Calendar event with a Meet link.

        Args:
            summary: The event title.
            description: The event description.
            start_time: ISO 8601 format start time (e.g., "2025-10-31T09:00:00").
            end_time: ISO 8601 format end time (e.g., "2025-10-31T10:00:00").
            attendees: list of attendee email addresses.
            time_zone: The time zone for the event (e.g., "America/New_York").

        Returns:
            A dictionary containing event details (success=True, meet_link,
            event_link, event_id) or an error message (success=False, error).
        """
        if attendees is None:
            attendees = []

        request_id = f"meet-{datetime.now().timestamp()}-{hash(summary)}"
        logger.info(
            f"Creating event '{summary}' from {start_time} to {end_time} "
            f"with Meet link (request_id: {request_id})"
        )

        try:
            event_body: dict[str, Any] = {
                "summary": summary,
                "description": description,
                "start": {"dateTime": start_time, "timeZone": time_zone},
                "end": {"dateTime": end_time, "timeZone": time_zone},
                "conferenceData": {
                    "createRequest": {
                        "requestId": request_id,
                        "conferenceSolutionKey": {"type": "hangoutsMeet"}
                    }
                },
                "attendees": [{"email": email} for email in attendees],
            }

            created_event = (
                self.calendar_service.events()
                .insert(
                    calendarId=self.calendar_id,
                    body=event_body,
                    conferenceDataVersion=1,
                )
                .execute()
            )

            logger.info(f"Successfully created event (ID: {created_event.get('id')})")
            return {
                "success": True,
                "meet_link": created_event.get("hangoutLink"),
                "event_link": created_event.get("htmlLink"),
                "event_id": created_event.get("id"),
            }

        except HttpError as e:
            logger.error(
                f"HttpError while creating event '{summary}': {e}", exc_info=True
            )
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(
                f"Unexpected error while creating event '{summary}': {e}",
                exc_info=True
            )
            return {"success": False, "error": f"An unexpected error occurred: {e}"}


# --- Global Client Instance ---
# This creates a single, module-level client instance when the script is imported.
# It will automatically handle authentication when initialized.
google_calendar_client: Optional[GoogleCalendarClient] = None
try:
    google_calendar_client = GoogleCalendarClient()
except Exception as e:
    # Error is already logged by the __init__ method
    logger.critical(
        "Global GoogleCalendarClient instance failed to initialize. "
        "The global create_calendar_event_with_meet function will not work."
    )


# --- Global Function Wrapper ---
def create_calendar_event_with_meet(
        summary: str,
        description: str,
        start_time: str,
        end_time: str,
        attendees: Optional[list[str]] = None
) -> dict[str, Any]:
    """Global wrapper to create a calendar event using the global client.

    This provides an easy-to-call function that mirrors the original script's
    functionality, but now uses the encapsulated class instance.

    Args:
        summary: The event title.
        description: The event description.
        start_time: ISO 8601 format start time.
        end_time: ISO 8601 format end time.
        attendees: list of attendee email addresses.

    Returns:
        A dictionary containing event details or an error.
    """
    if google_calendar_client:
        return google_calendar_client.create_calendar_event_with_meet(
            summary, description, start_time, end_time, attendees
        )
    else:
        logger.error(
            "create_calendar_event_with_meet called but global client is not initialized."
        )
        return {"success": False, "error": "Google Calendar client not initialized."}


# --- Example Usage ---
if __name__ == "__main__":
    """
    This block runs only when the script is executed directly.
    It demonstrates how to use the global function.
    """
    logger.info("\n--- Running Example Usage ---")
    if google_calendar_client:
        # Get current time in the local timezone and format for the API
        # We'll schedule an event for 1 hour, 1 day from now.
        try:
            now = datetime.now().astimezone()
            start_event = (now + timedelta(days=1)).replace(microsecond=0)
            end_event = (start_event + timedelta(hours=1))

            start_iso = start_event.isoformat()
            end_iso = end_event.isoformat()

            logger.info(
                f"Attempting to create a test event from {start_iso} to {end_iso}..."
            )

            event_details = create_calendar_event_with_meet(
                summary="Test Event from Refactored Client",
                description="This is a test event created by the new class-based script.",
                start_time=start_iso,
                end_time=end_iso,
                attendees=["test.user@example.com"]  # Add a dummy attendee
            )

            if event_details.get("success"):
                logger.info("\n--- Event Created Successfully ---")
                logger.info(f"Event Link: {event_details.get('event_link')}")
                logger.info(f"Meet Link: {event_details.get('meet_link')}")
                logger.info(f"Event ID: {event_details.get('event_id')}")
            else:
                logger.error("\n--- Error Creating Event ---")
                logger.error(f"Error: {event_details.get('error')}")

        except Exception as e:
            logger.critical(f"Error during example run: {e}", exc_info=True)
    else:
        logger.warning(
            "Could not run example: Global client failed to initialize."
        )
