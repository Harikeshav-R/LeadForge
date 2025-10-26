import datetime

from pydantic import BaseModel, Field


class TwilioRecordingPayload(BaseModel):
    recording_url: str = Field(..., alias="RecordingUrl")
    recording_sid: str = Field(..., alias="RecordingSid")
    call_sid: str = Field(..., alias="CallSid")
    recording_status: str = Field(..., alias="RecordingStatus")
    recording_duration: str | None = Field(None, alias="RecordingDuration")


class PhoneAnalysisOutput(BaseModel):
    success: bool = Field(..., description="True if the phone analysis was successful, False otherwise.")
    client_interested_in_meeting: bool = Field(False, description="Whether the client is interested in the meeting.")
    meeting_time: datetime.datetime | None = Field(None, description="The time of the meeting, if any.")
