import uuid

from pydantic import BaseModel, Field

from app.schemas.mail import Mail


class StateBase(BaseModel):
    client_name: str = Field(..., description="The name of the client.")
    client_email: str = Field(..., description="The email of the client.")

    sender_name: str = Field(..., description="The name of the sender.")
    sender_title: str = Field(..., description="The job title of the sender.")

    website_critique: str = Field(...,
                                  description="A detailed analysis of the critical issues and outdated elements of their current website.")
    demo_url: str = Field(...,
                          description="The link to the new, modern prototype website our agency has built for them.")
    web_agency_name: str = Field(..., description="The name of the web agency.")
    web_agency_logo: str = Field(..., description="The URL of the web agency logo.")

    email_contents: Mail | None = Field(None, description="The email contents to send.")
    email_sent: bool = Field(False, description="Whether the email has been sent.")


class StateCreate(StateBase):
    pass


class StateUpdate(BaseModel):
    web_agency_name: str | None = Field(None, description="The name of the web agency.")
    web_agency_logo: str | None = Field(None, description="The URL of the web agency logo.")
    sender_name: str | None = Field(None, description="The name of the sender.")
    sender_title: str | None = Field(None, description="The job title of the sender.")
    website_critique: str | None = Field(None,
                                         description="A detailed analysis of the critical issues and outdated elements of their current website.")
    demo_url: str | None = Field(None,
                                 description="The link to the new, modern prototype website our agency has built for them.")
    email_contents: Mail | None = Field(None, description="The email contents to send.")
    email_sent: bool | None = Field(None, description="Whether the email has been sent.")


class State(StateBase):
    id: uuid.UUID = Field(uuid.uuid4, description="ID of the state.")

    class Config:
        from_attributes = True
